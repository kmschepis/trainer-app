import logging
import os
from typing import Optional

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

logger = logging.getLogger("trainer2.api.db")


def _async_database_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("DATABASE_URL is required")

    # Prefer asyncpg for runtime.
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def init_db(app: FastAPI) -> None:
    engine: AsyncEngine = create_async_engine(
        _async_database_url(),
        pool_size=5,
        max_overflow=0,
        pool_pre_ping=True,
    )
    app.state.db_engine = engine
    app.state.db_sessionmaker = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    logger.info("db initialized")


async def close_db(app: FastAPI) -> None:
    engine: Optional[AsyncEngine] = getattr(app.state, "db_engine", None)
    if engine is not None:
        await engine.dispose()
        app.state.db_engine = None
        app.state.db_sessionmaker = None
        logger.info("db engine disposed")


def get_sessionmaker(app: FastAPI) -> async_sessionmaker[AsyncSession]:
    sessionmaker = getattr(app.state, "db_sessionmaker", None)
    if sessionmaker is None:
        raise RuntimeError("db sessionmaker is not initialized")
    return sessionmaker
