from __future__ import annotations

import os
import time
import uuid
from typing import Any, Dict, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.deps import get_uow
from app.passwords import hash_password, verify_password
from app.repositories.users_repo import UsersRepository
from app.uow import UnitOfWork

router = APIRouter(tags=["auth"])


def _jwt_secret() -> str:
    secret = os.getenv("AUTH_JWT_SECRET", "").strip()
    if not secret:
        raise HTTPException(status_code=500, detail="AUTH_JWT_SECRET not configured")
    return secret


def _issue_token(*, user_id: uuid.UUID, email: Optional[str], name: Optional[str]) -> str:
    now = int(time.time())
    payload: Dict[str, Any] = {
        "iss": "trainer2-api",
        "aud": "trainer2-api",
        "iat": now,
        "exp": now + 60 * 60 * 24 * 7,
        "sub": str(user_id),
        "provider": "local",
        "email": email,
        "name": name,
    }
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)


class AuthResponse(BaseModel):
    userId: str
    email: Optional[str] = None
    name: Optional[str] = None
    accessToken: str


def get_users_repo() -> UsersRepository:
    return UsersRepository()


@router.post("/auth/register", response_model=AuthResponse)
async def register(
    payload: RegisterRequest,
    uow: UnitOfWork = Depends(get_uow),
    users: UsersRepository = Depends(get_users_repo),
) -> AuthResponse:
    email = payload.email.strip().lower()
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    try:
        user_id = await users.create_local_user(
            uow.session,
            email=email,
            password_hash=password_hash,
            name=(payload.name.strip() if isinstance(payload.name, str) else None),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    await uow.commit()
    token = _issue_token(user_id=user_id, email=email, name=payload.name)
    return AuthResponse(userId=str(user_id), email=email, name=payload.name, accessToken=token)


@router.post("/auth/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    uow: UnitOfWork = Depends(get_uow),
    users: UsersRepository = Depends(get_users_repo),
) -> AuthResponse:
    email = payload.email.strip().lower()
    user = await users.get_by_provider_subject(uow.session, provider="local", provider_subject=email)
    if user is None or not user.password_hash:
        raise HTTPException(status_code=401, detail="invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    token = _issue_token(user_id=user.id, email=user.email, name=user.name)
    return AuthResponse(userId=str(user.id), email=user.email, name=user.name, accessToken=token)
