from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    userId: str
    sessionId: str
    runId: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None
    maxTurns: int = Field(default=10, ge=1, le=50)
