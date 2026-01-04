from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
    ) -> "ChatResponse":
        # Persist the user message.
        await self._events.append_event(
            type="ChatMessageSent",
            payload={"role": "user", "text": message},
            session_id=session_id,
        )

        ui_actions: List[Dict[str, Any]] = []
        tool_calls: List[ToolCall] = []

        onboarding = context.get("onboarding") if isinstance(context, dict) else None
        has_profile = context.get("hasProfile") if isinstance(context, dict) else None

        if not has_profile and not (isinstance(onboarding, dict) and onboarding.get("open")):
            ui_actions.append({"type": "ui.onboarding.open"})

        if message == "ONBOARDING_SUBMIT" and isinstance(onboarding, dict) and onboarding.get("submit"):
            draft = onboarding.get("draft")
            if isinstance(draft, dict):
                tool_calls.append(ToolCall(id=str(uuid.uuid4()), name="profile.save", args=draft))
                ui_actions.append({"type": "ui.onboarding.close"})
                ui_actions.append({"type": "ui.toast", "message": "Profile saved."})
                text = "Profile saved. What are you training today?"
            else:
                text = "I couldn't read the onboarding form payload. Please try submitting again."
        else:
            # Call the agent.
            result = await self._agent.respond(session_id=session_id, message=message, context=context)
            text = str(result.get("text", ""))
            actions = result.get("a2uiActions", [])
            if isinstance(actions, list):
                ui_actions.extend([a for a in actions if isinstance(a, dict)])

        # Persist the assistant message.
        await self._events.append_event(
            type="ChatMessageSent",
            payload={"role": "assistant", "text": text},
            session_id=session_id,
        )

        return ChatResponse(text=text, a2ui_actions=ui_actions, tool_calls=tool_calls)


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    args: Dict[str, Any]


@dataclass(frozen=True)
class ChatResponse:
    text: str
    a2ui_actions: List[Dict[str, Any]]
    tool_calls: List[ToolCall]
