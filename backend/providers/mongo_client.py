"""MongoDB persistence for investigations and saved reports."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
except ModuleNotFoundError:  # pragma: no cover - handled at runtime
    MongoClient = None
    Collection = Any


_client: Any | None = None


def _collection(name: str) -> Collection | None:
    uri = os.getenv("MONGODB_URI")
    if not uri or MongoClient is None:
        return None

    global _client
    if _client is None:
        _client = MongoClient(uri, serverSelectionTimeoutMS=2500)

    db_name = os.getenv("MONGODB_DB", "hermes_x")
    return _client[db_name][name]


def enabled() -> bool:
    return bool(os.getenv("MONGODB_URI")) and MongoClient is not None


def save_investigation(record: dict[str, Any]) -> dict[str, Any]:
    collection = _collection("investigations")
    if collection is None:
        return {"stored": False, "reason": "mongodb_not_configured"}

    doc = dict(record)
    doc.setdefault("created_at", datetime.now(UTC).isoformat())
    collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
    return {"stored": True, "id": doc["id"]}


def list_investigations(limit: int = 50) -> list[dict[str, Any]]:
    collection = _collection("investigations")
    if collection is None:
        return []

    docs = collection.find({}, {"_id": False}).sort("created_at", -1).limit(limit)
    return list(docs)


def save_report(record: dict[str, Any]) -> dict[str, Any]:
    collection = _collection("saved_reports")
    if collection is None:
        return {"stored": False, "reason": "mongodb_not_configured"}

    doc = dict(record)
    doc.setdefault("saved_at", datetime.now(UTC).isoformat())
    collection.update_one({"id": doc["id"]}, {"$set": doc}, upsert=True)
    return {"stored": True, "id": doc["id"]}


def list_reports(limit: int = 50) -> list[dict[str, Any]]:
    collection = _collection("saved_reports")
    if collection is None:
        return []

    docs = collection.find({}, {"_id": False}).sort("saved_at", -1).limit(limit)
    return list(docs)
