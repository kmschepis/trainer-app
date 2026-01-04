from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.events import Event, now_utc
from app.models import EventRow


class EventsRepository:
    async def append(
        self,
        session: AsyncSession,
        *,
        type: str,
        payload: dict,
        session_id: Optional[str],
    ) -> Event:
        event_id = uuid.uuid4()
        ts = now_utc()

        row = EventRow(
            id=event_id,
            ts=ts,
            type=type,
            session_id=session_id,
            payload=payload,
        )
        session.add(row)
        await session.flush()

        return Event(
            id=str(event_id),
            ts=ts,
            type=type,
            sessionId=session_id,
            payload=payload,
        )

    async def list_all(self, session: AsyncSession) -> List[Event]:
        stmt = select(EventRow).order_by(EventRow.ts.asc(), EventRow.id.asc())
        result = await session.execute(stmt)
        rows = result.scalars().all()

        events: List[Event] = []
        for r in rows:
            events.append(
                Event(
                    id=str(r.id),
                    ts=r.ts,
                    type=r.type,
                    sessionId=r.session_id,
                    payload=dict(r.payload),
                )
            )
        return events
