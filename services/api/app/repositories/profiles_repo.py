from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ProfileRow


class ProfilesRepository:
    async def get_by_user(self, session: AsyncSession, *, user_id: uuid.UUID) -> Optional[ProfileRow]:
        stmt = select(ProfileRow).where(ProfileRow.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def upsert_by_user(
        self,
        session: AsyncSession,
        *,
        user_id: uuid.UUID,
        now,
        values: dict,
    ) -> ProfileRow:
        existing = await self.get_by_user(session, user_id=user_id)
        if existing:
            for k, v in values.items():
                setattr(existing, k, v)
            existing.updated_at = now
            await session.flush()
            return existing

        row = ProfileRow(id=uuid.uuid4(), user_id=user_id, created_at=now, updated_at=now, **values)
        session.add(row)
        await session.flush()
        return row

    async def delete_by_user(self, session: AsyncSession, *, user_id: uuid.UUID) -> bool:
        existing = await self.get_by_user(session, user_id=user_id)
        if not existing:
            return False
        await session.delete(existing)
        await session.flush()
        return True
