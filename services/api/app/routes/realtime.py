from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.clients.agent_client import AgentClient
from app.auth import AuthUser, authenticate_token
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

    timeout = httpx.Timeout(connect=10.0, read=None, write=10.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as http:
        agent = AgentClient(base_url=agent_base_url, http=http)
        repo = EventsRepository()
        profiles_repo = ProfilesRepository()
        sessionmaker = get_sessionmaker(ws.app)
        events = EventsService(sessionmaker=sessionmaker, repo=repo)
        profiles = ProfilesService(sessionmaker=sessionmaker, repo=profiles_repo)
        chat = ChatService(events=events)

        try:
            while True:
                raw = await ws.receive_text()

                try:
                    msg = parse_client_envelope(raw)
                except ValueError as exc:
                    await ws.send_json(
                        {
                            "type": "RUN_ERROR",
                            "message": str(exc),
                        }
                    )
                    continue

                ws_messages_total.labels(type="run").inc()

                thread_id = msg.thread_id
                run_id = msg.run_id

                await ws.send_json(
                    {
                        "type": "RUN_STARTED",
                        "threadId": thread_id,
                        "runId": run_id,
                        "parentRunId": msg.parent_run_id,
                    }
                )

                try:
                    started = time.perf_counter()
                    ui_context: Dict[str, Any] | None = None
                    if msg.forwarded_props and isinstance(msg.forwarded_props.get("uiContext"), dict):
                        ui_context = msg.forwarded_props.get("uiContext")

                    # Persist the user message.
                    await chat.persist_user_message(user_id=user.id, session_id=thread_id, message=msg.message)

                    # Load state snapshot for this session/thread.
                    async with sessionmaker() as session:
                        past_events = await repo.list_by_user_session(
                            session, user_id=user.id, session_id=thread_id
                        )
                    snapshot = project_state(past_events)

                    # Prefer SQL-backed profile over event-sourced payload.
                    profile = await profiles.get_profile_dict(user_id=user.id)
                    if profile is not None:
                        snapshot["profile"] = profile

                    context_payload: Dict[str, Any] = {"ui": ui_context or {}, "state": snapshot}

                    final_text_parts: list[str] = []
                    errored = False

                    async for evt in agent.run_stream(
                        user_id=str(user.id),
                        session_id=thread_id,
                        message=msg.message,
                        context=context_payload,
                        max_turns=10,
                    ):
                        etype = evt.get("type")

                        if etype == "RUN_ERROR":
                            errored = True
                            await ws.send_json(
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
                            await ws.send_json(out)
                            continue

                        if etype == "TEXT_MESSAGE_CHUNK":
                            delta = evt.get("delta")
                            if isinstance(delta, str) and delta.strip():
                                final_text_parts.append(delta)
                            await ws.send_json(evt)
                            continue

                        # Ignore agent's RUN_FINISHED; API emits RUN_FINISHED with thread/run ids.

                    if errored:
                        agent_calls_total.labels(status="error").inc()
                        continue

                    agent_calls_total.labels(status="success").inc()
                    agent_call_duration_seconds.observe(time.perf_counter() - started)
                except Exception as exc:
                    agent_calls_total.labels(status="error").inc()
                    await ws.send_json(
                        {
                            "type": "RUN_ERROR",
                            "threadId": thread_id,
                            "runId": run_id,
                            "message": f"chat backend failed: {exc}",
                        }
                    )
                    logger.exception(
                        "chat backend failed",
                        extra={"threadId": thread_id, "runId": run_id},
                    )
                    continue

                final_text = "\n\n".join(final_text_parts).strip() or "OK."
                await chat.persist_assistant_message(user_id=user.id, session_id=thread_id, text=final_text)

                await ws.send_json(
                    {
                        "type": "RUN_FINISHED",
                        "threadId": thread_id,
                        "runId": run_id,
                    }
                )
        except WebSocketDisconnect:
            return
