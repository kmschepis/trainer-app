from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple


SendJsonFn = Callable[[Dict[str, Any]], Awaitable[None]]


@dataclass
class StageDecision:
    approved: bool
    payload_edits: Optional[Dict[str, Any]] = None
    reason: str = ""


@dataclass
class AssistantDecision:
    approved: bool
    final_text: str = ""
    reason: str = ""


@dataclass
class ToolDecision:
    approved: bool
    args_override: Optional[Dict[str, Any]] = None
    reason: str = ""


@dataclass
class AuditPolicy:
    auto_approve_tool_calls: bool = False

    @staticmethod
    def from_forwarded_props(forwarded_props: Optional[Dict[str, Any]]) -> "AuditPolicy":
        if not forwarded_props or not isinstance(forwarded_props, dict):
            return AuditPolicy()
        policy = forwarded_props.get("auditPolicy")
        if not isinstance(policy, dict):
            return AuditPolicy()

        auto_tools = policy.get("autoApproveToolCalls")
        return AuditPolicy(auto_approve_tool_calls=bool(auto_tools))


@dataclass
class AuditRunSession:
    user_id: uuid.UUID
    thread_id: str
    run_id: str
    send_json: SendJsonFn
    policy: AuditPolicy
    created_at: float = field(default_factory=lambda: time.time())

    stage_future: "asyncio.Future[StageDecision]" = field(default_factory=asyncio.Future)
    assistant_future: "asyncio.Future[AssistantDecision]" = field(default_factory=asyncio.Future)
    tool_futures: Dict[str, "asyncio.Future[ToolDecision]"] = field(default_factory=dict)


class AuditCoordinator:
    """In-memory approval coordinator for /coach_audit.

    Notes:
    - This is a single-process, in-memory coordinator (good for dev / MVP).
    - If you run multiple API workers, approvals won't coordinate across processes.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._runs: Dict[Tuple[uuid.UUID, str, str], AuditRunSession] = {}

    async def start_run(
        self,
        *,
        user_id: uuid.UUID,
        thread_id: str,
        run_id: str,
        send_json: SendJsonFn,
        policy: AuditPolicy,
    ) -> AuditRunSession:
        key = (user_id, thread_id, run_id)
        async with self._lock:
            session = AuditRunSession(
                user_id=user_id,
                thread_id=thread_id,
                run_id=run_id,
                send_json=send_json,
                policy=policy,
            )
            self._runs[key] = session
            return session

    async def get_run(self, *, user_id: uuid.UUID, thread_id: str, run_id: str) -> Optional[AuditRunSession]:
        key = (user_id, thread_id, run_id)
        async with self._lock:
            return self._runs.get(key)

    async def end_run(self, *, user_id: uuid.UUID, thread_id: str, run_id: str) -> None:
        key = (user_id, thread_id, run_id)
        async with self._lock:
            self._runs.pop(key, None)

    async def resolve_stage(
        self,
        *,
        user_id: uuid.UUID,
        thread_id: str,
        run_id: str,
        decision: StageDecision,
    ) -> bool:
        session = await self.get_run(user_id=user_id, thread_id=thread_id, run_id=run_id)
        if not session:
            return False
        if session.stage_future.done():
            return False
        session.stage_future.set_result(decision)
        return True

    async def resolve_assistant(
        self,
        *,
        user_id: uuid.UUID,
        thread_id: str,
        run_id: str,
        decision: AssistantDecision,
    ) -> bool:
        session = await self.get_run(user_id=user_id, thread_id=thread_id, run_id=run_id)
        if not session:
            return False
        if session.assistant_future.done():
            return False
        session.assistant_future.set_result(decision)
        return True

    async def resolve_tool(
        self,
        *,
        user_id: uuid.UUID,
        thread_id: str,
        run_id: str,
        tool_call_id: str,
        decision: ToolDecision,
    ) -> bool:
        session = await self.get_run(user_id=user_id, thread_id=thread_id, run_id=run_id)
        if not session:
            return False
        fut = session.tool_futures.get(tool_call_id)
        if not fut or fut.done():
            return False
        fut.set_result(decision)
        return True

    async def await_tool_decision(
        self,
        *,
        user_id: uuid.UUID,
        thread_id: str,
        run_id: str,
        tool_call_id: str,
    ) -> Optional[ToolDecision]:
        session = await self.get_run(user_id=user_id, thread_id=thread_id, run_id=run_id)
        if not session:
            return None
        fut = session.tool_futures.get(tool_call_id)
        if not fut:
            fut = asyncio.Future()
            session.tool_futures[tool_call_id] = fut
        return await fut


audit_coordinator = AuditCoordinator()
