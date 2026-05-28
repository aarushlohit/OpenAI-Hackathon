"""Shared document helpers for MongoDB records."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from bson import ObjectId


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def public_user(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(doc.get("_id")),
        "name": doc.get("name", ""),
        "email": doc.get("email", ""),
        "theme": doc.get("theme", "dark"),
        "created_at": doc.get("created_at"),
    }


def object_id(value: str) -> ObjectId:
    return ObjectId(value)
