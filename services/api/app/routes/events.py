from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import AuthUser, get_current_user
from app.events import project_state
from app.repositories.events_repo import EventsRepository
from app.repositories.profiles_repo import ProfilesRepository
from app.services.profiles_service import profile_row_to_dict
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


def get_profiles_repo() -> ProfilesRepository:
    return ProfilesRepository()


@router.post("/events", response_model=EventAck)
async def append_event(
    event: EventIn,
    uow: UnitOfWork = Depends(get_uow),
    repo: EventsRepository = Depends(get_events_repo),
    user: AuthUser = Depends(get_current_user),
) -> EventAck:
    created = await repo.append(
        uow.session,
        type=event.type,
        payload=event.payload,
        user_id=user.id,
        session_id=event.sessionId,
    )
    await uow.commit()
    return EventAck(id=created.id, ts=created.ts.isoformat(), type=created.type)


@router.get("/state")
async def get_state(
    sessionId: Optional[str] = None,
    uow: UnitOfWork = Depends(get_uow),
    repo: EventsRepository = Depends(get_events_repo),
    profiles_repo: ProfilesRepository = Depends(get_profiles_repo),
    user: AuthUser = Depends(get_current_user),
) -> Dict[str, Any]:
    if sessionId:
        events = await repo.list_by_user_session(uow.session, user_id=user.id, session_id=sessionId)
    else:
        events = await repo.list_by_user(uow.session, user_id=user.id)
    snapshot = project_state(events)

    row = await profiles_repo.get_by_user(uow.session, user_id=user.id)
    if row is not None:
        snapshot["profile"] = profile_row_to_dict(row)
    last = events[-1] if events else None
    return {
        "meta": {
            "eventsCount": len(events),
            "lastEventId": last.id if last else None,
            "lastEventTs": last.ts.isoformat() if last else None,
        },
        "snapshot": snapshot,
    }
