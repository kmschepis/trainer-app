from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ClientChatSend:
    request_id: Optional[str]
    session_id: Optional[str]
    message: str
    context: Optional[Dict[str, Any]]


@dataclass(frozen=True)
class ClientPing:
    request_id: Optional[str]


def parse_client_envelope(raw: str) -> ClientPing | ClientChatSend:
    """Parse/validate inbound websocket messages.

    Keeps FastAPI/WebSocket code focused on orchestration.

    Expected shapes:
    - {"type":"ping","requestId": "..."}
    - {"type":"chat.send","sessionId":"...","message":"...","context":{...},"requestId":"..."}

    Raises ValueError with a user-friendly error message.
    """

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("invalid json")

    if not isinstance(payload, dict):
        raise ValueError("invalid payload")

    msg_type = payload.get("type")
    request_id = payload.get("requestId")
    if request_id is not None and not isinstance(request_id, str):
        request_id = None

    if msg_type == "ping":
        return ClientPing(request_id=request_id)

    if msg_type != "chat.send":
        raise ValueError(f"unsupported type: {msg_type}")

    session_id = payload.get("sessionId")
    if session_id is not None and not isinstance(session_id, str):
        session_id = None

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")

    context = payload.get("context")
    if context is not None and not isinstance(context, dict):
        context = None

    return ClientChatSend(
        request_id=request_id,
        session_id=session_id,
        message=message,
        context=context,
    )
