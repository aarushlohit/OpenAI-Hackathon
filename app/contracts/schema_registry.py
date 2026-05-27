from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field

from app.contracts.event_versions import CURRENT_EVENT_VERSION
from app.events.models import EventName


class RegisteredSchema(BaseModel):
    event: EventName
    version: str = CURRENT_EVENT_VERSION
    schema_hash: str = Field(min_length=12)


class SchemaRegistry:
    def __init__(self) -> None:
        self._schemas: dict[tuple[EventName, str], RegisteredSchema] = {}

    def register(self, event: EventName, payload_shape: dict[str, Any], version: str = CURRENT_EVENT_VERSION) -> RegisteredSchema:
        schema_hash = self.hash_schema(payload_shape)
        schema = RegisteredSchema(event=event, version=version, schema_hash=schema_hash)
        self._schemas[(event, version)] = schema
        return schema

    def get(self, event: EventName, version: str = CURRENT_EVENT_VERSION) -> RegisteredSchema | None:
        return self._schemas.get((event, version))

    def validate(self, event: EventName, version: str, schema_hash: str) -> bool:
        registered = self.get(event, version)
        return registered is None or registered.schema_hash == schema_hash

    def hash_schema(self, payload_shape: dict[str, Any]) -> str:
        encoded = repr(sorted(payload_shape.items())).encode("utf-8")
        return sha256(encoded).hexdigest()

