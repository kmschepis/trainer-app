from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Any, Optional

import jwt
from fastapi import Header, HTTPException, Request


@dataclass(frozen=True)
class AuthUser:
    id: uuid.UUID
    provider: str
    subject: str
    email: Optional[str]
    name: Optional[str]


def verify_google_id_token(id_token: str) -> dict[str, Any]:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if not client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID not configured")

    try:
        from google.auth.transport.requests import Request as GoogleRequest
        from google.oauth2 import id_token as google_id_token

        return google_id_token.verify_oauth2_token(id_token, GoogleRequest(), audience=client_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")


async def authenticate_google_token(app: Any, token: str) -> AuthUser:
    claims = verify_google_id_token(token)

    sub = str(claims.get("sub") or "").strip()
    if not sub:
        raise HTTPException(status_code=401, detail="invalid token")

    email = claims.get("email")
    name = claims.get("name")
    picture = claims.get("picture")

    # Create/find user id in our DB.
    from app.db import get_sessionmaker
    from app.repositories.users_repo import UsersRepository
    from app.uow import UnitOfWork

    sessionmaker = get_sessionmaker(app)
    async with sessionmaker() as session:
        async with UnitOfWork(session) as uow:
            user_id = await UsersRepository().upsert_google_user(
                uow.session,
                sub=sub,
                email=str(email) if isinstance(email, str) else None,
                name=str(name) if isinstance(name, str) else None,
                picture=str(picture) if isinstance(picture, str) else None,
            )
            await uow.commit()

    return AuthUser(
        id=user_id,
        provider="google",
        subject=sub,
        email=str(email) if isinstance(email, str) else None,
        name=str(name) if isinstance(name, str) else None,
    )


def _try_authenticate_local_jwt(token: str) -> AuthUser | None:
    secret = os.getenv("AUTH_JWT_SECRET", "").strip()
    if not secret:
        return None
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="trainer2-api",
            issuer="trainer2-api",
        )
    except Exception:
        return None

    sub = claims.get("sub")
    if not isinstance(sub, str):
        return None
    try:
        user_id = uuid.UUID(sub)
    except Exception:
        return None

    email = claims.get("email")
    name = claims.get("name")
    return AuthUser(
        id=user_id,
        provider="local",
        subject=sub,
        email=str(email) if isinstance(email, str) else None,
        name=str(name) if isinstance(name, str) else None,
    )


async def authenticate_token(app: Any, token: str) -> AuthUser:
    local = _try_authenticate_local_jwt(token)
    if local is not None:
        return local

    # Fall back to Google if configured.
    try:
        return await authenticate_google_token(app, token)
    except HTTPException as exc:
        # If Google isn't configured, treat this as unauthenticated.
        if exc.status_code == 500 and "GOOGLE_CLIENT_ID" in str(exc.detail):
            raise HTTPException(status_code=401, detail="invalid token")
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token")


async def get_current_user(request: Request, authorization: str | None = Header(default=None)) -> AuthUser:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="missing bearer token")

    return await authenticate_token(request.app, token)
