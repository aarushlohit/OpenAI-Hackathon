"""Async MongoDB connection for auth and user-owned app data."""

from __future__ import annotations

import os
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: AsyncIOMotorClient | None = None


def enabled() -> bool:
    return bool(os.getenv("MONGODB_URI"))


def client() -> AsyncIOMotorClient | None:
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=3000)
    return _client


def database() -> AsyncIOMotorDatabase | None:
    mongo = client()
    if mongo is None:
        return None
    return mongo[os.getenv("MONGODB_DB", "hermes_x")]


async def ensure_indexes() -> None:
    db = database()
    if db is None:
        return
    await db.users.create_index("email", unique=True)
    await db.sessions.create_index("user_id")
    await db.investigations.create_index([("user_id", 1), ("created_at", -1)])
    await db.saved_reports.create_index([("user_id", 1), ("saved_at", -1)])
    await db.uploaded_metadata.create_index([("user_id", 1), ("created_at", -1)])


def require_database() -> AsyncIOMotorDatabase:
    db = database()
    if db is None:
        raise RuntimeError("MongoDB is not configured")
    return db
