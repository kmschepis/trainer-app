from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.clients.agent_client import AgentClient
from app.auth import AuthUser, authenticate_token
from app.audit.coordinator import (
    AssistantDecision,
    AuditPolicy,
    StageDecision,
    ToolDecision,
    audit_coordinator,
)
from app.db import get_sessionmaker
from app.events import project_state
from app.metrics import agent_call_duration_seconds, agent_calls_total, ws_messages_total
from app.protocol import parse_client_envelope
from app.repositories.events_repo import EventsRepository
from app.repositories.profiles_repo import ProfilesRepository
from app.services.chat_service import ChatService
from app.services.events_service import EventsService
from app.services.profiles_service import ProfilesService

router = APIRouter(tags=["realtime"])

logger = logging.getLogger("trainer2.api.realtime")


@router.websocket("/realtime")
async def realtime(ws: WebSocket) -> None:
    await ws.accept()

    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=4401)
        return
    try:
        user: AuthUser = await authenticate_token(ws.app, token)
    except Exception:
        await ws.close(code=4401)
        return

    agent_base_url = os.getenv("AGENT_BASE_URL", "http://agent:9000")

    mode = (ws.query_params.get("mode") or "").strip().lower() or "chat"
    is_audit_mode = mode == "audit"

    timeout = httpx.Timeout(connect=10.0, read=None, write=10.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as http:
        agent = AgentClient(base_url=agent_base_url, http=http)
        repo = EventsRepository()
        profiles_repo = ProfilesRepository()
        sessionmaker = get_sessionmaker(ws.app)
        events = EventsService(sessionmaker=sessionmaker, repo=repo)
        profiles = ProfilesService(sessionmaker=sessionmaker, repo=profiles_repo)
        chat = ChatService(events=events)

        send_lock = asyncio.Lock()

        async def safe_send(payload: Dict[str, Any]) -> None:
            async with send_lock:
                await ws.send_json(payload)

        incoming: "asyncio.Queue[str]" = asyncio.Queue()

        async def recv_loop() -> None:
            while True:
                raw_text = await ws.receive_text()
                await incoming.put(raw_text)

        run_task: Optional[asyncio.Task[None]] = None
        recv_task = asyncio.create_task(recv_loop())

        async def process_run(raw: str) -> None:
            try:
                msg = parse_client_envelope(raw)
            except ValueError as exc:
                await safe_send({"type": "RUN_ERROR", "message": str(exc)})
                return

            ws_messages_total.labels(type="run").inc()
            thread_id = msg.thread_id
            run_id = msg.run_id

            ui_context: Dict[str, Any] | None = None
            if msg.forwarded_props and isinstance(msg.forwarded_props.get("uiContext"), dict):
                ui_context = msg.forwarded_props.get("uiContext")

            policy = AuditPolicy.from_forwarded_props(msg.forwarded_props)
            audit_session = None

            try:
                started = time.perf_counter()

                # Persist the user message immediately so the left chat thread shows it.
                await chat.persist_user_message(user_id=user.id, session_id=thread_id, message=msg.message)

                # Load state snapshot for this session/thread.
                async with sessionmaker() as session:
                    past_events = await repo.list_by_user_session(
                        session, user_id=user.id, session_id=thread_id
                    )
                # Do not include chat message history in the model context.
                non_chat_events = [e for e in past_events if e.type != "ChatMessageSent"]
                snapshot = project_state(non_chat_events)

                # Prefer SQL-backed profile over event-sourced payload.
                profile = await profiles.get_profile_dict(user_id=user.id)
                if profile is not None:
                    snapshot["profile"] = profile

                context_payload: Dict[str, Any] = {"ui": ui_context or {}, "state": snapshot}

                if is_audit_mode:
                    audit_session = await audit_coordinator.start_run(
                        user_id=user.id,
                        thread_id=thread_id,
                        run_id=run_id,
                        send_json=safe_send,
                        policy=policy,
                    )

                    await safe_send(
                        {
                            "type": "RUN_STAGED",
                            "threadId": thread_id,
                            "runId": run_id,
                            "payload": {
                                "message": msg.message,
                                "context": context_payload,
                                "forwardedProps": msg.forwarded_props or {},
                            },
                        }
                    )

                    decision = await audit_session.stage_future
                    if not decision.approved:
                        await safe_send(
                            {
                                "type": "RUN_STAGE_DENIED",
                                "threadId": thread_id,
                                "runId": run_id,
                                "reason": decision.reason or "denied",
                            }
                        )
                        await safe_send({"type": "RUN_FINISHED", "threadId": thread_id, "runId": run_id})
                        return

                    message_override = None
                    context_override = None
                    if decision.payload_edits and isinstance(decision.payload_edits, dict):
                        if isinstance(decision.payload_edits.get("message"), str):
                            message_override = decision.payload_edits.get("message")
                        if isinstance(decision.payload_edits.get("context"), dict):
                            context_override = decision.payload_edits.get("context")

                    final_message = (message_override or msg.message).strip()
                    final_context = context_override or context_payload

                    await safe_send(
                        {
                            "type": "RUN_STAGE_APPROVED",
                            "threadId": thread_id,
                            "runId": run_id,
                            "payloadEdits": decision.payload_edits or None,
                        }
                    )
                    await safe_send(
                        {
                            "type": "RUN_STARTED",
                            "threadId": thread_id,
                            "runId": run_id,
                            "parentRunId": msg.parent_run_id,
                        }
                    )
                else:
                    await safe_send(
                        {
                            "type": "RUN_STARTED",
                            "threadId": thread_id,
                            "runId": run_id,
                            "parentRunId": msg.parent_run_id,
                        }
                    )
                    final_message = msg.message
                    final_context = context_payload

                final_text_parts: list[str] = []
                errored = False

                async for evt in agent.run_stream(
                    user_id=str(user.id),
                    session_id=thread_id,
                    run_id=run_id if is_audit_mode else None,
                    message=final_message,
                    context=final_context,
                    max_turns=10,
                ):
                    etype = evt.get("type")

                    if etype == "RUN_ERROR":
                        errored = True
                        await safe_send(
                            {
                                "type": "RUN_ERROR",
                                "threadId": thread_id,
                                "runId": run_id,
                                "message": evt.get("message") or "agent_failed",
                            }
                        )
                        break

                    if etype in ("TOOL_CALL_STARTED", "TOOL_CALL_RESULT"):
                        out = dict(evt)
                        out["threadId"] = thread_id
                        out["runId"] = run_id
                        await safe_send(out)
                        continue

                    if etype == "TEXT_MESSAGE_CHUNK":
                        delta = evt.get("delta")
                        if isinstance(delta, str) and delta.strip():
                            final_text_parts.append(delta)
                        if not is_audit_mode:
                            await safe_send(evt)
                        continue

                if errored:
                    agent_calls_total.labels(status="error").inc()
                    return

                agent_calls_total.labels(status="success").inc()
                agent_call_duration_seconds.observe(time.perf_counter() - started)

                draft_text = "\n\n".join(final_text_parts).strip() or "OK."

                if is_audit_mode and audit_session is not None:
                    await safe_send(
                        {
                            "type": "ASSISTANT_DRAFT_PROPOSED",
                            "threadId": thread_id,
                            "runId": run_id,
                            "draftText": draft_text,
                        }
                    )
                    a_decision = await audit_session.assistant_future
                    if not a_decision.approved:
                        await safe_send(
                            {
                                "type": "ASSISTANT_FINAL_DENIED",
                                "threadId": thread_id,
                                "runId": run_id,
                                "reason": a_decision.reason or "denied",
                            }
                        )
                        await safe_send({"type": "RUN_FINISHED", "threadId": thread_id, "runId": run_id})
                        return

                    final_text = (a_decision.final_text or draft_text).strip() or "OK."
                    await chat.persist_assistant_message(user_id=user.id, session_id=thread_id, text=final_text)
                    await safe_send({"type": "TEXT_MESSAGE_CHUNK", "delta": final_text})
                    await safe_send(
                        {
                            "type": "ASSISTANT_FINAL_APPROVED",
                            "threadId": thread_id,
                            "runId": run_id,
                            "finalText": final_text,
                        }
                    )
                    await safe_send({"type": "RUN_FINISHED", "threadId": thread_id, "runId": run_id})
                    return

                await chat.persist_assistant_message(user_id=user.id, session_id=thread_id, text=draft_text)
                await safe_send({"type": "RUN_FINISHED", "threadId": thread_id, "runId": run_id})
            except Exception as exc:
                agent_calls_total.labels(status="error").inc()
                await safe_send(
                    {
                        "type": "RUN_ERROR",
                        "threadId": (locals().get("thread_id") or ""),
                        "runId": (locals().get("run_id") or ""),
                        "message": f"chat backend failed: {exc}",
                    }
                )
                logger.exception(
                    "chat backend failed",
                    extra={"threadId": locals().get("thread_id"), "runId": locals().get("run_id")},
                )
            finally:
                if audit_session is not None:
                    await audit_coordinator.end_run(user_id=user.id, thread_id=audit_session.thread_id, run_id=audit_session.run_id)

        def _try_parse_json(raw: str) -> Optional[Dict[str, Any]]:
            try:
                data: Any = json.loads(raw)
            except Exception:
                return None
            if isinstance(data, dict):
                return data
            return None

        try:
            while True:
                raw = await incoming.get()

                parsed = _try_parse_json(raw)
                msg_type = parsed.get("type") if parsed else None
                if isinstance(msg_type, str):
                    ws_messages_total.labels(type="approval").inc()

                    thread_id = parsed.get("threadId")
                    run_id = parsed.get("runId")
                    if not isinstance(thread_id, str) or not isinstance(run_id, str):
                        continue

                    if msg_type == "RUN_STAGE_APPROVED":
                        payload_edits = parsed.get("payloadEdits")
                        if payload_edits is not None and not isinstance(payload_edits, dict):
                            payload_edits = None
                        await audit_coordinator.resolve_stage(
                            user_id=user.id,
                            thread_id=thread_id,
                            run_id=run_id,
                            decision=StageDecision(approved=True, payload_edits=payload_edits),
                        )
                        continue

                    if msg_type == "RUN_STAGE_DENIED":
                        reason = parsed.get("reason") if isinstance(parsed.get("reason"), str) else ""
                        await audit_coordinator.resolve_stage(
                            user_id=user.id,
                            thread_id=thread_id,
                            run_id=run_id,
                            decision=StageDecision(approved=False, reason=reason),
                        )
                        continue

                    if msg_type == "TOOL_CALL_APPROVED":
                        tool_call_id = parsed.get("toolCallId")
                        if not isinstance(tool_call_id, str) or not tool_call_id.strip():
                            continue
                        args_override = parsed.get("argsOverride")
                        if args_override is not None and not isinstance(args_override, dict):
                            args_override = None
                        await audit_coordinator.resolve_tool(
                            user_id=user.id,
                            thread_id=thread_id,
                            run_id=run_id,
                            tool_call_id=tool_call_id,
                            decision=ToolDecision(approved=True, args_override=args_override),
                        )
                        continue

                    if msg_type == "TOOL_CALL_DENIED":
                        tool_call_id = parsed.get("toolCallId")
                        if not isinstance(tool_call_id, str) or not tool_call_id.strip():
                            continue
                        reason = parsed.get("reason") if isinstance(parsed.get("reason"), str) else ""
                        await audit_coordinator.resolve_tool(
                            user_id=user.id,
                            thread_id=thread_id,
                            run_id=run_id,
                            tool_call_id=tool_call_id,
                            decision=ToolDecision(approved=False, reason=reason),
                        )
                        continue

                    if msg_type == "ASSISTANT_FINAL_APPROVED":
                        final_text = parsed.get("finalText") if isinstance(parsed.get("finalText"), str) else ""
                        await audit_coordinator.resolve_assistant(
                            user_id=user.id,
                            thread_id=thread_id,
                            run_id=run_id,
                            decision=AssistantDecision(approved=True, final_text=final_text),
                        )
                        continue

                    if msg_type == "ASSISTANT_FINAL_DENIED":
                        reason = parsed.get("reason") if isinstance(parsed.get("reason"), str) else ""
                        await audit_coordinator.resolve_assistant(
                            user_id=user.id,
                            thread_id=thread_id,
                            run_id=run_id,
                            decision=AssistantDecision(approved=False, reason=reason),
                        )
                        continue

                if run_task is not None and not run_task.done():
                    await safe_send({"type": "RUN_ERROR", "message": "run already in progress"})
                    continue

                run_task = asyncio.create_task(process_run(raw))
        except WebSocketDisconnect:
            return
        finally:
            recv_task.cancel()
