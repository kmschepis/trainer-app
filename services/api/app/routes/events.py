from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.events import project_state
from app.repositories.events_repo import EventsRepository
from app.uow import UnitOfWork
from app.deps import get_uow

router = APIRouter(tags=["events"])


class EventIn(BaseModel):
    type: str = Field(min_length=1)
    payload: Dict[str, Any]
    sessionId: Optional[str] = None


class EventAck(BaseModel):
    id: str
    ts: str
    type: str


def get_events_repo() -> EventsRepository:
    return EventsRepository()


@router.post("/events", response_model=EventAck)
async def append_event(
    event: EventIn,
    uow: UnitOfWork = Depends(get_uow),
    repo: EventsRepository = Depends(get_events_repo),
) -> EventAck:
    created = await repo.append(
        uow.session,
        type=event.type,
        payload=event.payload,
        session_id=event.sessionId,
    )
    await uow.commit()
    return EventAck(id=created.id, ts=created.ts.isoformat(), type=created.type)


@router.get("/state")
async def get_state(
    uow: UnitOfWork = Depends(get_uow),
    repo: EventsRepository = Depends(get_events_repo),
) -> Dict[str, Any]:
    events = await repo.list_all(uow.session)
    snapshot = project_state(events)
    last = events[-1] if events else None
    return {
        "meta": {
            "eventsCount": len(events),
            "lastEventId": last.id if last else None,
            "lastEventTs": last.ts.isoformat() if last else None,
        },
        "snapshot": snapshot,
    }
