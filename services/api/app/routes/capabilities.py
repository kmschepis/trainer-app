from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Header, HTTPException

from app.agent_auth import require_agent_auth
from app.agentic.openai_tools import openai_tools
from app.agentic.table_cards import generate_table_card_markdown
from app.resources.registry import RESOURCE_DEFS

router = APIRouter(tags=["capabilities"])


def _table_cards() -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for key, r in RESOURCE_DEFS.items():
        md = generate_table_card_markdown(
            name=r.name,
            model=r.model,
            meaning=r.meaning,
            primary_key=r.primary_key,
            tool_mapping=r.tool_mapping,
            verification=[
                "After any write, verify via read-back (get/list) before claiming success.",
            ],
        )
        cards.append(
            {
                "id": key,
                "name": r.name,
                "primaryKey": r.primary_key,
                "meaning": r.meaning,
                "markdown": md,
            }
        )
    return cards


@router.get("/capabilities")
def capabilities(authorization: str | None = Header(default=None)) -> Dict[str, Any]:
    require_agent_auth(authorization)

    tools = openai_tools()
    table_cards = _table_cards()

    # A stable-ish hash for change detection.
    payload = {
        "tools": tools,
        "tableCards": table_cards,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    sha256 = hashlib.sha256(raw).hexdigest()

    return {
        "version": 1,
        "generatedAt": int(time.time()),
        "sha256": sha256,
        "tools": tools,
        "tableCards": table_cards,
    }
