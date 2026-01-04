from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any, Dict

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.clients.agent_client import AgentClient
from app.db import get_sessionmaker
from app.metrics import agent_call_duration_seconds, agent_calls_total, ws_messages_total
from app.protocol import parse_client_envelope
from app.repositories.events_repo import EventsRepository
from app.services.chat_service import ChatService
from app.services.events_service import EventsService
from app.services.tools_service import ToolExecutionError, ToolsService

router = APIRouter(tags=["realtime"])

logger = logging.getLogger("trainer2.api.realtime")


@router.websocket("/realtime")
async def realtime(ws: WebSocket) -> None:
    await ws.accept()

    agent_base_url = os.getenv("AGENT_BASE_URL", "http://agent:9000")

    async with httpx.AsyncClient(timeout=10.0) as http:
        agent = AgentClient(base_url=agent_base_url, http=http)
        events = EventsService(sessionmaker=get_sessionmaker(ws.app), repo=EventsRepository())
        chat = ChatService(agent=agent, events=events)
        tools = ToolsService(events=events)

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

                    chat_resp = await chat.handle_user_message(
                        session_id=thread_id,
                        message=msg.message,
                        context=ui_context,
                    )

                    if chat_resp.tool_calls:
                        for call in chat_resp.tool_calls:
                            await ws.send_json(
                                {
                                    "type": "TOOL_CALL_STARTED",
                                    "threadId": thread_id,
                                    "runId": run_id,
                                    "toolCallId": call.id,
                                    "toolName": call.name,
                                    "args": call.args,
                                }
                            )

                            try:
                                result = await tools.execute(
                                    session_id=thread_id,
                                    name=call.name,
                                    args=call.args,
                                )
                            except ToolExecutionError as exc:
                                raise RuntimeError(f"tool failed: {exc}")

                            await ws.send_json(
                                {
                                    "type": "TOOL_CALL_RESULT",
                                    "threadId": thread_id,
                                    "runId": run_id,
                                    "toolCallId": call.id,
                                    "toolName": call.name,
                                    "result": result,
                                }
                            )
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

                message_id = str(uuid.uuid4())
                await ws.send_json(
                    {
                        "type": "TEXT_MESSAGE_CHUNK",
                        "messageId": message_id,
                        "role": "assistant",
                        "delta": chat_resp.text,
                    }
                )

                if isinstance(chat_resp.a2ui_actions, list) and chat_resp.a2ui_actions:
                    for action in chat_resp.a2ui_actions:
                        await ws.send_json(
                            {
                                "type": "CUSTOM",
                                "name": "ui.action",
                                "value": action,
                            }
                        )

                await ws.send_json(
                    {
                        "type": "RUN_FINISHED",
                        "threadId": thread_id,
                        "runId": run_id,
                    }
                )
        except WebSocketDisconnect:
            return
