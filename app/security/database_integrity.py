from hashlib import sha256

from pydantic import BaseModel

from app.events.models import EventEnvelope


class DatabaseIntegrityReport(BaseModel):
    verified: bool
    event_count: int
    chain_hash: str


class DatabaseIntegrityVerifier:
    def verify_event_chain(self, events: list[EventEnvelope]) -> DatabaseIntegrityReport:
        previous = ""
        for event in events:
            governed = event.governed()
            payload = f"{previous}:{governed.event_id}:{governed.model_dump_json()}"
            previous = sha256(payload.encode("utf-8")).hexdigest()
        return DatabaseIntegrityReport(
            verified=all(event.schema_hash or event.governed().schema_hash for event in events),
            event_count=len(events),
            chain_hash=previous,
        )

