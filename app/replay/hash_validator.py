from hashlib import sha256

from app.events.models import EventEnvelope
from app.replay.replay_engine import ReplaySession


class HashValidator:
    def event_hash(self, event: EventEnvelope) -> str:
        return sha256(event.model_dump_json().encode("utf-8")).hexdigest()

    def payload_hash(self, payload: str) -> str:
        return sha256(payload.encode("utf-8")).hexdigest()

    def validate_session(self, session: ReplaySession) -> bool:
        return all(frame.integrity_hash == self.event_hash(frame.event) for frame in session.frames)

