"""Auth API routes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from pymongo.errors import DuplicateKeyError

from auth.jwt_handler import create_access_token
from auth.middleware import require_user
from auth.password_utils import hash_password, verify_password
from database.models import now_iso, public_user
from database.mongodb import require_database

router = APIRouter(prefix="/auth", tags=["auth"])


def _db_or_503():
    try:
        return require_database()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="MongoDB is not configured") from exc


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=256)


class PreferencesRequest(BaseModel):
    theme: str = Field(pattern="^(dark|light)$")


async def _issue_session(user: dict[str, Any]) -> dict[str, Any]:
    db = _db_or_503()
    token, expires_at, session_id = create_access_token(str(user["_id"]), user["email"])
    await db.sessions.insert_one({
        "id": session_id,
        "user_id": str(user["_id"]),
        "email": user["email"],
        "created_at": now_iso(),
        "expires_at": expires_at.isoformat(),
    })
    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "user": public_user(user),
    }


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, response: Response):
    db = _db_or_503()
    doc = {
        "name": payload.name.strip(),
        "email": payload.email.lower(),
        "password_hash": hash_password(payload.password),
        "created_at": now_iso(),
        "theme": "light",
    }
    try:
        result = await db.users.insert_one(doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="An account already exists for this email") from exc
    doc["_id"] = result.inserted_id
    session = await _issue_session(doc)
    response.set_cookie(
        "hermes_token",
        session["token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=24 * 60 * 60,
    )
    return session


@router.post("/login")
async def login(payload: LoginRequest, response: Response):
    db = _db_or_503()
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    session = await _issue_session(user)
    response.set_cookie(
        "hermes_token",
        session["token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=24 * 60 * 60,
    )
    return session


@router.get("/me")
async def me(user: dict[str, Any] = Depends(require_user)):
    return {"user": user}


@router.patch("/preferences")
async def preferences(payload: PreferencesRequest, user: dict[str, Any] = Depends(require_user)):
    db = _db_or_503()
    await db.users.update_one({"email": user["email"]}, {"$set": {"theme": payload.theme}})
    user["theme"] = payload.theme
    return {"user": user}


@router.post("/logout")
async def logout(response: Response, user: dict[str, Any] = Depends(require_user)):
    db = _db_or_503()
    await db.sessions.update_many(
        {"user_id": user["id"], "revoked_at": {"$exists": False}},
        {"$set": {"revoked_at": datetime.now(UTC).isoformat()}},
    )
    response.delete_cookie("hermes_token")
    return {"ok": True}
