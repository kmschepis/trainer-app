from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.events import now_utc
from app.repositories.profiles_repo import ProfilesRepository
from app.uow import UnitOfWork


PROFILE_FIELD_MAP: dict[str, str] = {
    "firstName": "first_name",
    "lastName": "last_name",
    "email": "email",
    "phone": "phone",
    "goals": "goals",
    "experience": "experience",
    "constraints": "constraints",
    "equipment": "equipment",
    "injuriesOrRiskFlags": "injuries_or_risk_flags",
    "dietPrefs": "diet_prefs",
}

METRICS_FIELD_MAP: dict[str, str] = {
    "age": "metrics_age",
    "height": "metrics_height",
    "weight": "metrics_weight",
}


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return s if s else None
    return None


def profile_row_to_dict(row) -> Dict[str, Any]:
    profile: Dict[str, Any] = {}
    for api_key, column in PROFILE_FIELD_MAP.items():
        profile[api_key] = getattr(row, column) or ""

    metrics: Dict[str, Any] = {}
    for api_key, column in METRICS_FIELD_MAP.items():
        metrics[api_key] = getattr(row, column) or ""
    profile["metrics"] = metrics

    return profile


class ProfilesService:
    def __init__(
        self,
        *,
        sessionmaker: async_sessionmaker[AsyncSession],
        repo: ProfilesRepository,
    ):
        self._sessionmaker = sessionmaker
        self._repo = repo

    async def get_profile_dict(self, *, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        async with self._sessionmaker() as session:
            row = await self._repo.get_by_user(session, user_id=user_id)
            return profile_row_to_dict(row) if row else None

    async def upsert_from_payload(self, *, user_id: uuid.UUID, payload: Dict[str, Any]) -> Dict[str, Any]:
        metrics = payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {}
        now = now_utc()

        values: Dict[str, Any] = {}
        for api_key, column in PROFILE_FIELD_MAP.items():
            values[column] = _clean_str(payload.get(api_key))
        for api_key, column in METRICS_FIELD_MAP.items():
            values[column] = _clean_str(metrics.get(api_key))

        async with self._sessionmaker() as session:
            async with UnitOfWork(session) as uow:
                row = await self._repo.upsert_by_user(
                    uow.session,
                    user_id=user_id,
                    now=now,
                    values=values,
                )
                await uow.commit()

            return profile_row_to_dict(row)

    async def delete(self, *, user_id: uuid.UUID) -> bool:
        async with self._sessionmaker() as session:
            async with UnitOfWork(session) as uow:
                deleted = await self._repo.delete_by_user(uow.session, user_id=user_id)
                await uow.commit()
                return deleted
