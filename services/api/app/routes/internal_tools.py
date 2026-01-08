from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.agent_auth import require_agent_auth
from app.db import get_sessionmaker
from app.repositories.events_repo import EventsRepository
from app.repositories.profiles_repo import ProfilesRepository
from app.services.events_service import EventsService
from app.services.profiles_service import ProfilesService
from app.services.tools_service import ToolExecutionError, ToolsService

router = APIRouter(tags=["internal-tools"])
logger = logging.getLogger("trainer2.api.internal_tools")


class ToolExecuteRequest(BaseModel):
    userId: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)
    name: str = Field(min_length=1)
    args: Dict[str, Any] = Field(default_factory=dict)


@router.post("/internal/tools/execute")
async def execute_tool(
    payload: ToolExecuteRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    require_agent_auth(authorization)

    try:
        user_id = uuid.UUID(payload.userId)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid userId")

    session_id = payload.sessionId
    name = payload.name
    args = payload.args if isinstance(payload.args, dict) else {}

    repo = EventsRepository()
    profiles_repo = ProfilesRepository()
    sessionmaker = get_sessionmaker(request.app)
    events = EventsService(sessionmaker=sessionmaker, repo=repo)
    profiles = ProfilesService(sessionmaker=sessionmaker, repo=profiles_repo)
    tools = ToolsService(events=events, profiles=profiles)

    try:
        return await tools.execute(user_id=user_id, session_id=session_id, name=name, args=args)
    except ToolExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
