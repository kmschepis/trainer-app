from __future__ import annotations

import uuid
from typing import Any, Dict

from app.services.events_service import EventsService
from app.services.profiles_service import ProfilesService


class ToolExecutionError(RuntimeError):
    pass


class ToolsService:
    def __init__(self, *, events: EventsService, profiles: ProfilesService):
        self._events = events
        self._profiles = profiles

    async def execute(
        self,
        *,
        user_id: uuid.UUID,
        session_id: str,
        name: str,
        args: Dict[str, Any],
    ) -> Dict[str, Any]:
        if name in ("profile.get", "profile_get"):
            profile = await self._profiles.get_profile_dict(user_id=user_id)
            return {"profile": profile}

        if name in ("profile.save", "profile_save"):
            if not isinstance(args, dict):
                raise ToolExecutionError("profile.save args must be an object")
            payload = args.get("profile") if "profile" in args and isinstance(args.get("profile"), dict) else args

            saved_profile = await self._profiles.upsert_from_payload(user_id=user_id, payload=payload)
            await self._events.append_event(
                type="ProfileSaved", payload=saved_profile, user_id=user_id, session_id=session_id
            )
            return {"ok": True, "profile": saved_profile}

        if name in ("profile.delete", "profile_delete"):
            await self._profiles.delete(user_id=user_id)
            await self._events.append_event(
                type="ProfileDeleted", payload={}, user_id=user_id, session_id=session_id
            )
            return {"ok": True}

        raise ToolExecutionError(f"unknown tool: {name}")
