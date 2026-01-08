from __future__ import annotations

import uuid
from typing import Any, Callable, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories.events_repo import EventsRepository
from app.uow import UnitOfWork


class EventsService:
    def __init__(
        self,
        *,
        sessionmaker: async_sessionmaker[AsyncSession],
        repo: EventsRepository,
    ):
        self._sessionmaker = sessionmaker
        self._repo = repo

    async def append_event(
        self,
        *,
        type: str,
        payload: Dict[str, Any],
        user_id: Optional[uuid.UUID],
        session_id: Optional[str],
    ) -> None:
        async with self._sessionmaker() as session:
            async with UnitOfWork(session) as uow:
                await self._repo.append(
                    uow.session,
                    type=type,
                    payload=payload,
                    user_id=user_id,
                    session_id=session_id,
                )
                await uow.commit()
