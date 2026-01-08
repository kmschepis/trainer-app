from __future__ import annotations

import uuid
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.events import now_utc
from app.models import UserRow


class UsersRepository:
    async def upsert_google_user(
        self,
        session: AsyncSession,
        *,
        sub: str,
        email: Optional[str],
        name: Optional[str],
        picture: Optional[str],
    ) -> uuid.UUID:
        user_id = uuid.uuid4()

        stmt = (
            insert(UserRow)
            .values(
                id=user_id,
                provider="google",
                provider_subject=sub,
                email=email,
                name=name,
                image_url=picture,
                created_at=now_utc(),
            )
            .on_conflict_do_update(
                index_elements=[UserRow.provider, UserRow.provider_subject],
                set_={
                    "email": email,
                    "name": name,
                    "image_url": picture,
                },
            )
            .returning(UserRow.id)
        )

        result = await session.execute(stmt)
        row = result.first()
        if not row:
            raise RuntimeError("failed to upsert user")
        return row[0]

    async def get_by_provider_subject(
        self,
        session: AsyncSession,
        *,
        provider: str,
        provider_subject: str,
    ) -> UserRow | None:
        result = await session.execute(
            sa.select(UserRow).where(
                (UserRow.provider == provider) & (UserRow.provider_subject == provider_subject)
            )
        )
        return result.scalars().first()

    async def create_local_user(
        self,
        session: AsyncSession,
        *,
        email: str,
        password_hash: str,
        name: str | None = None,
    ) -> uuid.UUID:
        email_norm = email.strip().lower()
        if not email_norm:
            raise ValueError("email required")

        existing = await self.get_by_provider_subject(
            session,
            provider="local",
            provider_subject=email_norm,
        )
        if existing is not None:
            raise ValueError("user already exists")

        user_id = uuid.uuid4()
        row = UserRow(
            id=user_id,
            provider="local",
            provider_subject=email_norm,
            email=email_norm,
            name=name,
            image_url=None,
            password_hash=password_hash,
            created_at=now_utc(),
        )
        session.add(row)
        return user_id
