from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ClientRunAgentInput:
    """Minimal subset of AG-UI RunAgentInput for our WebSocket transport.

    We treat each incoming message as a new run within a thread.
    """

    thread_id: str
    run_id: str
    parent_run_id: Optional[str]
    message: str
    forwarded_props: Optional[Dict[str, Any]]


def parse_client_envelope(raw: str) -> ClientRunAgentInput:
    """Parse/validate inbound websocket messages.

    We accept an AG-UI-compatible RunAgentInput shape over WebSockets.

    Expected minimal shape:
    - {"threadId": "...", "runId": "...", "message": "...", "forwardedProps": {...}}

    Raises ValueError with a user-friendly error message.
    """

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("invalid json")

    if not isinstance(payload, dict):
        raise ValueError("invalid payload")

    thread_id = payload.get("threadId")
    if not isinstance(thread_id, str) or not thread_id.strip():
        raise ValueError("threadId must be a non-empty string")

    run_id = payload.get("runId")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("runId must be a non-empty string")

    parent_run_id = payload.get("parentRunId")
    if parent_run_id is not None and not isinstance(parent_run_id, str):
        parent_run_id = None

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")

    forwarded_props = payload.get("forwardedProps")
    if forwarded_props is not None and not isinstance(forwarded_props, dict):
        forwarded_props = None

    return ClientRunAgentInput(
        thread_id=thread_id,
        run_id=run_id,
        parent_run_id=parent_run_id,
        message=message,
        forwarded_props=forwarded_props,
    )
