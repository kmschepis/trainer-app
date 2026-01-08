from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.agent_auth import require_agent_auth
from app.audit.coordinator import ToolDecision, audit_coordinator


router = APIRouter(tags=["internal-audit"])


class ToolAwaitRequest(BaseModel):
    userId: str = Field(min_length=1)
    sessionId: str = Field(min_length=1)
    runId: str = Field(min_length=1)
    toolName: str = Field(min_length=1)
    args: Dict[str, Any] = Field(default_factory=dict)
    toolCallId: Optional[str] = None


@router.post("/internal/audit/tool/await")
async def await_tool_approval(
    payload: ToolAwaitRequest,
    request: Request,
    authorization: str | None = Header(default=None),
) -> Dict[str, Any]:
    require_agent_auth(authorization)

    try:
        user_id = uuid.UUID(payload.userId)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid userId")

    thread_id = payload.sessionId
    run_id = payload.runId
    tool_name = payload.toolName
    args = payload.args if isinstance(payload.args, dict) else {}
    tool_call_id = (payload.toolCallId or "").strip() or str(uuid.uuid4())

    session = await audit_coordinator.get_run(user_id=user_id, thread_id=thread_id, run_id=run_id)
    if not session:
        return {"approved": True, "toolCallId": tool_call_id, "args": args}

    known_tools = {"profile_get", "profile_save", "profile_delete"}
    if tool_name not in known_tools:
        return {
            "approved": False,
            "toolCallId": tool_call_id,
            "reason": f"unknown tool: {tool_name}",
        }

    if session.policy.auto_approve_tool_calls:
        return {"approved": True, "toolCallId": tool_call_id, "args": args}

    await session.send_json(
        {
            "type": "TOOL_CALL_PROPOSED",
            "threadId": thread_id,
            "runId": run_id,
            "toolCallId": tool_call_id,
            "toolName": tool_name,
            "args": args,
            "label": "",
        }
    )

    decision = await audit_coordinator.await_tool_decision(
        user_id=user_id,
        thread_id=thread_id,
        run_id=run_id,
        tool_call_id=tool_call_id,
    )

    if decision is None:
        return {"approved": True, "toolCallId": tool_call_id, "args": args}

    if not decision.approved:
        await session.send_json(
            {
                "type": "TOOL_CALL_DENIED",
                "threadId": thread_id,
                "runId": run_id,
                "toolCallId": tool_call_id,
                "reason": decision.reason or "denied",
            }
        )
        return {
            "approved": False,
            "toolCallId": tool_call_id,
            "reason": decision.reason or "denied",
        }

    args_override = decision.args_override if isinstance(decision.args_override, dict) else None
    await session.send_json(
        {
            "type": "TOOL_CALL_APPROVED",
            "threadId": thread_id,
            "runId": run_id,
            "toolCallId": tool_call_id,
            "argsOverride": args_override,
        }
    )
    return {"approved": True, "toolCallId": tool_call_id, "args": args_override or args}
