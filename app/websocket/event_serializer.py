import json
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from app.events.models import EventEnvelope


class WebsocketEventPayload(BaseModel):
    event: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    agent: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    event_version: str = "1.0"
    schema_hash: str = ""
    producer: str = "hermes-x"
    trace: dict[str, Any] = Field(default_factory=dict)


class EventSerializer:
    def serialize(self, event: EventEnvelope) -> str:
        payload = WebsocketEventPayload.model_validate(event.safe_payload())
        return json.dumps(payload.model_dump(mode="json"), ensure_ascii=True)

    def deserialize(self, raw: str) -> WebsocketEventPayload:
        try:
            data = json.loads(raw)
            return WebsocketEventPayload.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as error:
            raise ValueError("Malformed websocket event payload") from error
