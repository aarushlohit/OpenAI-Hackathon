"""JWT creation and validation."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

JWT_ALGORITHM = "HS256"


def _secret() -> str:
    return os.getenv("JWT_SECRET") or "dev-only-change-me"


def create_access_token(user_id: str, email: str) -> tuple[str, datetime, str]:
    expires = datetime.now(UTC) + timedelta(hours=int(os.getenv("JWT_EXPIRE_HOURS", "24")))
    session_id = str(uuid4())
    payload = {
        "sub": user_id,
        "email": email,
        "sid": session_id,
        "exp": expires,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM), expires, session_id


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])
