"""Authentication dependencies."""

from __future__ import annotations

from typing import Any

import jwt
from fastapi import Depends, Header, HTTPException, status

from auth.jwt_handler import decode_access_token
from database.models import object_id, public_user
from database.mongodb import database


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


async def optional_user(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    token = _bearer_token(authorization)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        return None

    db = database()
    if db is None:
        return None
    user = await db.users.find_one({"_id": object_id(payload["sub"])})
    return public_user(user) if user else None


async def require_user(user: dict[str, Any] | None = Depends(optional_user)) -> dict[str, Any]:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user
