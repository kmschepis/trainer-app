from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, Optional

import httpx


class AgentClient:
    def __init__(self, *, base_url: str, http: httpx.AsyncClient):
        self._base_url = base_url.rstrip("/")
        self._http = http

    async def run_stream(
        self,
        *,
        user_id: str,
        session_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        max_turns: int = 10,
    ) -> AsyncIterator[Dict[str, Any]]:
        payload: Dict[str, Any] = {
            "userId": user_id,
            "sessionId": session_id,
            "message": message,
            "maxTurns": max_turns,
        }
        if context is not None:
            payload["context"] = context

        async with self._http.stream("POST", f"{self._base_url}/run", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.strip():
                    continue
                try:
                    data: Any = json.loads(line)
                except Exception:
                    continue
                if isinstance(data, dict):
                    yield data
