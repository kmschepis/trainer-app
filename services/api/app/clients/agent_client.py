from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class AgentClient:
    def __init__(self, *, base_url: str, http: httpx.AsyncClient):
        self._base_url = base_url.rstrip("/")
        self._http = http

    async def respond(
        self,
        *,
        session_id: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"sessionId": session_id, "message": message}
        if context is not None:
            payload["context"] = context

        resp = await self._http.post(f"{self._base_url}/respond", json=payload)
        resp.raise_for_status()
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("agent returned invalid response")
        return data
