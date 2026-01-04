from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.clients.agent_client import AgentClient
from app.services.events_service import EventsService


class ChatService:
    def __init__(self, *, agent: AgentClient, events: EventsService):
        self._agent = agent
        self._events = events

    async def handle_user_message(
        self,
        *,
        session_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        # Persist the user message.
        await self._events.append_event(
            type="ChatMessageSent",
            payload={"role": "user", "text": message},
            session_id=session_id,
        )

        # Call the agent.
        result = await self._agent.respond(session_id=session_id, message=message, context=context)
        text = str(result.get("text", ""))
        actions = result.get("a2uiActions", [])

        # Persist the assistant message.
        await self._events.append_event(
            type="ChatMessageSent",
            payload={"role": "assistant", "text": text},
            session_id=session_id,
        )

        if not isinstance(actions, list):
            actions = []
        return text, actions
