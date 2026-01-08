from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from app.capabilities_sync import load_tools_from_generated


def _instructions_root() -> Path:
    return Path(__file__).parent / "instructions"


def load_agent_markdown(*, agent_name: str) -> str:
    path = _instructions_root() / "agents" / f"{agent_name}.md"
    return path.read_text(encoding="utf-8")


def _tools_index_block(tools: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for t in tools:
        fn = t.get("function") if isinstance(t, dict) else None
        if not isinstance(fn, dict):
            continue
        name = fn.get("name")
        desc = fn.get("description")
        if isinstance(name, str) and name.strip():
            if isinstance(desc, str) and desc.strip():
                lines.append(f"- {name}: {desc.strip()}")
            else:
                lines.append(f"- {name}")
    return "\n".join(lines) if lines else "(no tools loaded)"


def _table_cards_block() -> str:
    cards_dir = Path(__file__).parent / "generated" / "table_cards"
    if not cards_dir.exists():
        return "(no table cards loaded)"

    parts: List[str] = []
    for path in sorted(cards_dir.glob("*.md")):
        try:
            parts.append(path.read_text(encoding="utf-8").rstrip() + "\n")
        except Exception:
            continue
    return "\n\n".join(parts).strip() if parts else "(no table cards loaded)"


def compile_coach_instructions() -> str:
    base = load_agent_markdown(agent_name="coach").strip()

    tools = load_tools_from_generated()

    return (
        base
        + "\n\n"
        + "## Tool Surface (from API /capabilities)\n"
        + _tools_index_block(tools)
        + "\n\n"
        + "## Table Cards (from API /capabilities)\n"
        + _table_cards_block()
        + "\n"
    )
