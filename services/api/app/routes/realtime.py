from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Optional

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.clients.agent_client import AgentClient
from app.db import get_sessionmaker
from app.metrics import agent_call_duration_seconds, agent_calls_total, ws_messages_total
from app.protocol import ClientChatSend, ClientPing, parse_client_envelope
from app.repositories.events_repo import EventsRepository
from app.services.chat_service import ChatService
from app.services.events_service import EventsService

router = APIRouter(tags=["realtime"])

logger = logging.getLogger("trainer2.api.realtime")


@router.websocket("/realtime")
async def realtime(ws: WebSocket) -> None:
    await ws.accept()

    agent_base_url = os.getenv("AGENT_BASE_URL", "http://agent:9000")

    session_id: Optional[str] = None
    async with httpx.AsyncClient(timeout=10.0) as http:
        agent = AgentClient(base_url=agent_base_url, http=http)
        events = EventsService(sessionmaker=get_sessionmaker(ws.app), repo=EventsRepository())
        chat = ChatService(agent=agent, events=events)

        try:
            while True:
                raw = await ws.receive_text()

                try:
                    msg = parse_client_envelope(raw)
                except ValueError as exc:
                    await ws.send_json({"type": "error", "message": str(exc)})
                    continue

                if isinstance(msg, ClientPing):
                    ws_messages_total.labels(type="ping").inc()
                    await ws.send_json({"type": "pong", "requestId": msg.request_id})
                    continue

                ws_messages_total.labels(type="chat.send").inc()

                request_id = msg.request_id
                if msg.session_id:
                    session_id = msg.session_id
                if not session_id:
                    session_id = str(uuid.uuid4())
                    await ws.send_json(
                        {"type": "session.created", "sessionId": session_id, "requestId": request_id}
                    )

                try:
                    started = time.perf_counter()
                    text, a2ui_actions = await chat.handle_user_message(
                        session_id=session_id,
                        message=msg.message,
                        context=msg.context,
                    )
                    agent_calls_total.labels(status="success").inc()
                    agent_call_duration_seconds.observe(time.perf_counter() - started)
                except Exception as exc:
                    agent_calls_total.labels(status="error").inc()
                    await ws.send_json(
                        {
                            "type": "error",
                            "sessionId": session_id,
                            "requestId": request_id,
                            "message": f"chat backend failed: {exc}",
                        }
                    )
                    logger.exception(
                        "chat backend failed",
                        extra={"sessionId": session_id, "requestId": request_id},
                    )
                    continue

                await ws.send_json(
                    {
                        "type": "chat.message",
                        "sessionId": session_id,
                        "role": "assistant",
                        "message": text,
                        "requestId": request_id,
                    }
                )

                if isinstance(a2ui_actions, list) and a2ui_actions:
                    for action in a2ui_actions:
                        await ws.send_json(
                            {
                                "type": "a2ui.action",
                                "sessionId": session_id,
                                "action": action,
                                "requestId": request_id,
                            }
                        )
        except WebSocketDisconnect:
            return
