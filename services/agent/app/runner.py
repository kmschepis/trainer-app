from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Optional

import httpx
from agents import Agent, RunConfig, Runner, function_tool
from agents.run_context import RunContextWrapper
from agents.stream_events import RunItemStreamEvent
from agents.items import ToolCallItem, ToolCallOutputItem

from app.capabilities_sync import _api_base_url, _sign_agent_jwt
from app.instructions_loader import compile_coach_instructions

logger = logging.getLogger("trainer2.agent.runner")


@dataclass
class RunCtx:
    api_base_url: str
    agent_jwt: str
    user_id: str
    session_id: str


async def _api_tool_execute(*, ctx: RunCtx, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)
    headers: Dict[str, str] = {}
    if ctx.agent_jwt:
        headers["Authorization"] = f"Bearer {ctx.agent_jwt}"

    async with httpx.AsyncClient(timeout=timeout) as http:
        resp = await http.post(
            f"{ctx.api_base_url}/internal/tools/execute",
            headers=headers,
            json={
                "userId": ctx.user_id,
                "sessionId": ctx.session_id,
                "name": name,
                "args": args,
            },
        )
        resp.raise_for_status()
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise RuntimeError("tool backend returned invalid response")
        return data


def _tool_labels() -> dict[str, str]:
    return {
        "profile_get": "Fetch the current user's onboarding profile.",
        "profile_save": "Save the user's onboarding profile (upsert).",
        "profile_delete": "Delete/clear the user's onboarding profile.",
    }


@function_tool(name_override="profile_get", description_override=_tool_labels()["profile_get"])
async def profile_get(ctx: RunContextWrapper[RunCtx]) -> Dict[str, Any]:
    return await _api_tool_execute(ctx=ctx.context, name="profile_get", args={})


@function_tool(
    name_override="profile_save",
    description_override=_tool_labels()["profile_save"],
    strict_mode=False,
)
async def profile_save(ctx: RunContextWrapper[RunCtx], profile: Dict[str, Any]) -> Dict[str, Any]:
    return await _api_tool_execute(ctx=ctx.context, name="profile_save", args={"profile": profile})


@function_tool(name_override="profile_delete", description_override=_tool_labels()["profile_delete"])
async def profile_delete(ctx: RunContextWrapper[RunCtx]) -> Dict[str, Any]:
    return await _api_tool_execute(ctx=ctx.context, name="profile_delete", args={})


@function_tool(
    name_override="ui_action",
    description_override=_tool_labels()["ui_action"],
    strict_mode=False,
)
async def ui_action(action: Dict[str, Any]) -> Dict[str, Any]:
    action_type = action.get("type") if isinstance(action, dict) else None
    if not isinstance(action_type, str) or not action_type.strip():
        return {"ok": False, "error": "ui_action requires action.type"}
    return {"ok": True}


def _coach_agent() -> Agent[RunCtx]:
    instructions = (compile_coach_instructions() or "").strip()
    if not instructions:
        raise RuntimeError("missing compiled instructions")

    return Agent(
        name="coach",
        instructions=instructions,
        tools=[profile_get, profile_save, profile_delete],
    )


def _context_prefix(context: Optional[Dict[str, Any]]) -> str:
    if not context or not isinstance(context, dict):
        return ""
    return "Context (JSON):\n" + json.dumps(context, ensure_ascii=False) + "\n\n"


async def run_stream(
    *,
    user_id: str,
    session_id: str,
    message: str,
    context: Optional[Dict[str, Any]],
    max_turns: int = 10,
) -> AsyncIterator[Dict[str, Any]]:
    """Run the coach agent and yield API-facing events (NDJSON-friendly dicts)."""

    if not message or not message.strip():
        yield {"type": "RUN_ERROR", "message": "missing message"}
        return

    api_base_url = _api_base_url()
    try:
        agent_jwt = _sign_agent_jwt()
    except Exception:
        agent_jwt = ""

    run_ctx = RunCtx(api_base_url=api_base_url, agent_jwt=agent_jwt, user_id=user_id, session_id=session_id)

    model = os.getenv("OPENAI_MODEL", "").strip() or None
    run_config = RunConfig(
        model=model,
        workflow_name="trainer2.agent.run",
        group_id=session_id,
        trace_metadata={"sessionId": session_id, "userId": user_id},
    )

    agent = _coach_agent()

    tool_labels = _tool_labels()
    call_id_to_name: dict[str, str] = {}

    try:
        streamed = Runner.run_streamed(
            agent,
            _context_prefix(context) + message.strip(),
            context=run_ctx,
            max_turns=max_turns,
            run_config=run_config,
        )

        async for evt in streamed.stream_events():
            if not isinstance(evt, RunItemStreamEvent):
                continue

            if evt.name == "tool_called" and isinstance(evt.item, ToolCallItem):
                raw = evt.item.raw_item
                call_id = getattr(raw, "call_id", None) or getattr(raw, "id", None)
                name = getattr(raw, "name", None)
                args_raw = getattr(raw, "arguments", None)

                if not isinstance(call_id, str) or not isinstance(name, str):
                    continue

                args: Dict[str, Any] = {}
                if isinstance(args_raw, str) and args_raw.strip():
                    try:
                        parsed = json.loads(args_raw)
                        if isinstance(parsed, dict):
                            args = parsed
                    except Exception:
                        args = {}

                call_id_to_name[call_id] = name
                yield {
                    "type": "TOOL_CALL_STARTED",
                    "toolCallId": call_id,
                    "toolName": name,
                    "label": tool_labels.get(name, ""),
                    "args": args,
                }

            if evt.name == "tool_output" and isinstance(evt.item, ToolCallOutputItem):
                raw = evt.item.raw_item
                call_id = raw.get("call_id") if isinstance(raw, dict) else None
                if not isinstance(call_id, str):
                    continue
                name = call_id_to_name.get(call_id, "")
                yield {
                    "type": "TOOL_CALL_RESULT",
                    "toolCallId": call_id,
                    "toolName": name,
                    "label": tool_labels.get(name, ""),
                    "result": evt.item.output,
                }

        final_text = ""
        try:
            final_text = streamed.final_output_as(str) or ""
        except Exception:
            final_text = ""

        message_id = str(uuid.uuid4())
        yield {
            "type": "TEXT_MESSAGE_CHUNK",
            "messageId": message_id,
            "role": "assistant",
            "delta": final_text.strip() or "OK.",
        }
        yield {"type": "RUN_FINISHED"}
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.exception("run_failed", extra={"sessionId": session_id})
        yield {"type": "RUN_ERROR", "message": f"agent_failed: {exc}"}
