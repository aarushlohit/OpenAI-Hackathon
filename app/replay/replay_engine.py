from datetime import datetime
from hashlib import sha256

from pydantic import BaseModel, Field

from app.events.models import EventEnvelope, EventName
from app.memory.investigation_repository import InvestigationRepository


class ReplayFrame(BaseModel):
    index: int = Field(ge=0)
    event: EventEnvelope
    offset_ms: int = Field(ge=0)
    integrity_hash: str = Field(default="", min_length=0)


class ReplaySession(BaseModel):
    investigation_id: str
    frames: list[ReplayFrame] = Field(default_factory=list)
    speed: float = Field(default=1.0, gt=0)


class ReplayEngine:
    def __init__(self, repository: InvestigationRepository) -> None:
        self._repository = repository

    async def build(self, investigation_id: str, speed: float = 1.0) -> ReplaySession:
        events = await self._repository.list_events(investigation_id)
        frames = self._frames(events)
        return ReplaySession(investigation_id=investigation_id, frames=frames, speed=speed)

    def _frames(self, events: list[EventEnvelope]) -> list[ReplayFrame]:
        if not events:
            return []
        started = events[0].timestamp
        return [
            ReplayFrame(
                index=index,
                event=event,
                offset_ms=self._offset_ms(started, event.timestamp),
                integrity_hash=self._hash_event(event),
            )
            for index, event in enumerate(events)
        ]

    def replay_event(self, frame: ReplayFrame) -> EventEnvelope:
        return frame.event.model_copy(update={"event": EventName.INVESTIGATION_REPLAY})

    def step(self, session: ReplaySession, index: int) -> ReplayFrame | None:
        if index < 0 or index >= len(session.frames):
            return None
        return session.frames[index]

    def verify(self, session: ReplaySession) -> bool:
        return all(frame.integrity_hash == self._hash_event(frame.event) for frame in session.frames)

    def _offset_ms(self, started: datetime, timestamp: datetime) -> int:
        return max(int((timestamp - started).total_seconds() * 1000), 0)

    def _hash_event(self, event: EventEnvelope) -> str:
        payload = event.model_dump_json()
        return sha256(payload.encode("utf-8")).hexdigest()

