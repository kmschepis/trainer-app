from __future__ import annotations

import uuid
from typing import Any, Dict

from app.services.events_service import EventsService


class ChatService:
    """Persistence helper for chat messages.

    The agent/tool/UI orchestration lives in the websocket route.
    """

    def __init__(self, *, events: EventsService):
        self._events = events

    async def persist_user_message(self, *, user_id: uuid.UUID, session_id: str, message: str) -> None:
        await self._events.append_event(
            type="ChatMessageSent",
            payload={"role": "user", "text": message},
            user_id=user_id,
            session_id=session_id,
        )

    async def persist_assistant_message(self, *, user_id: uuid.UUID, session_id: str, text: str) -> None:
        await self._events.append_event(
            type="ChatMessageSent",
            payload={"role": "assistant", "text": text},
            user_id=user_id,
            session_id=session_id,
        )

    async def persist_debug(self, *, user_id: uuid.UUID, session_id: str, payload: Dict[str, Any]) -> None:
        await self._events.append_event(
            type="Debug",
            payload=payload,
            user_id=user_id,
            session_id=session_id,
        )
