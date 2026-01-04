import logging
import os
from typing import Any, Optional

import asyncpg
from fastapi import FastAPI

logger = logging.getLogger("trainer2.api.db")


async def init_db(app: FastAPI) -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=5)
    app.state.db_pool = pool

    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
              id uuid PRIMARY KEY,
              ts timestamptz NOT NULL,
              type text NOT NULL,
              session_id text NULL,
              payload jsonb NOT NULL
            );
            """
        )
        await conn.execute("CREATE INDEX IF NOT EXISTS events_ts_idx ON events (ts);")
        await conn.execute("CREATE INDEX IF NOT EXISTS events_type_idx ON events (type);")

    logger.info("db initialized")


async def close_db(app: FastAPI) -> None:
    pool: Optional[asyncpg.Pool] = getattr(app.state, "db_pool", None)
    if pool is not None:
        await pool.close()
        app.state.db_pool = None
        logger.info("db pool closed")


def get_pool(app: FastAPI) -> asyncpg.Pool:
    pool = getattr(app.state, "db_pool", None)
    if pool is None:
        raise RuntimeError("db pool is not initialized")
    return pool
