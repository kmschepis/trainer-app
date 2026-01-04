from __future__ import annotations

from typing import Any, Dict

from app.services.events_service import EventsService


class ToolExecutionError(RuntimeError):
    pass


class ToolsService:
    def __init__(self, *, events: EventsService):
        self._events = events

    async def execute(
        self,
        *,
        session_id: str,
        name: str,
        args: Dict[str, Any],
    ) -> Dict[str, Any]:
        if name == "profile.save":
            if not isinstance(args, dict):
                raise ToolExecutionError("profile.save args must be an object")
            await self._events.append_event(type="ProfileSaved", payload=args, session_id=session_id)
            return {"ok": True}

        if name == "profile.delete":
            await self._events.append_event(type="ProfileDeleted", payload={}, session_id=session_id)
            return {"ok": True}

        raise ToolExecutionError(f"unknown tool: {name}")
