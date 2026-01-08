from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from pydantic import BaseModel

from app.resources.models import GoalResource, NoteResource, ProfileResource


@dataclass(frozen=True)
class ResourceDef:
    name: str
    model: Type[BaseModel]
    meaning: str
    primary_key: str
    tool_mapping: dict[str, str]


RESOURCE_DEFS: dict[str, ResourceDef] = {
    "profiles": ResourceDef(
        name="profiles",
        model=ProfileResource,
        meaning="User onboarding profile (demographic/contact + basic training context). One-to-one with users.",
        primary_key="user_id (UUID, unique)",
        tool_mapping={
            "Get": "profile_get({})",
            "Upsert": "profile_save({ profile: { ... } })",
            "Delete": "profile_delete({})",
        },
    ),
    "goals": ResourceDef(
        name="goals",
        model=GoalResource,
        meaning="User goals (many per user).",
        primary_key="id (UUID)",
        tool_mapping={},
    ),
    "notes": ResourceDef(
        name="notes",
        model=NoteResource,
        meaning="Coach notes (many per user), stored as markdown.",
        primary_key="id (UUID)",
        tool_mapping={},
    ),
}
