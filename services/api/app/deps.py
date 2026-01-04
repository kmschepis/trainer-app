from __future__ import annotations

from typing import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_sessionmaker
from app.uow import UnitOfWork


async def get_uow(request: Request) -> AsyncIterator[UnitOfWork]:
    SessionLocal = get_sessionmaker(request.app)
    session: AsyncSession = SessionLocal()
    async with UnitOfWork(session) as uow:
        yield uow
