from __future__ import annotations

import base64
import os

import jwt
from fastapi import HTTPException


def agent_auth_configured() -> bool:
    return bool(os.getenv("AGENT_PUBLIC_KEY", "").strip() or os.getenv("AGENT_PUBLIC_KEY_B64", "").strip())


def require_agent_auth(authorization: str | None) -> None:
    """Verify an agent-signed JWT (RS256) using AGENT_PUBLIC_KEY.

    If no agent public key is configured, this becomes a no-op (dev ergonomics).
    """

    pub_b64 = os.getenv("AGENT_PUBLIC_KEY_B64", "").strip()
    if pub_b64:
        try:
            pub = base64.b64decode(pub_b64.encode("utf-8")).decode("utf-8").strip()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"AGENT_PUBLIC_KEY_B64 invalid: {exc}")
    else:
        pub = os.getenv("AGENT_PUBLIC_KEY", "").strip()

    if not pub:
        # Dev mode: allow internal calls without JWT.
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="missing bearer token")

    try:
        jwt.decode(
            token,
            pub,
            algorithms=["RS256"],
            audience="trainer2-api",
            issuer="trainer2-agent",
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"invalid agent token: {exc}")
