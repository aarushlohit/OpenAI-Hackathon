from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.events.models import EventEnvelope


class DeadLetterEvent(BaseModel):
    reason: str = Field(min_length=1)
    event: EventEnvelope | None = None
    diagnostic: str | None = None
    quarantined_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DeadLetterQueue:
    def __init__(self, max_size: int = 500) -> None:
        self._max_size = max_size
        self._items: list[DeadLetterEvent] = []

    async def quarantine(self, item: DeadLetterEvent) -> None:
        self._items.append(item)
        if len(self._items) > self._max_size:
            self._items = self._items[-self._max_size :]

    async def list(self) -> list[DeadLetterEvent]:
        return list(self._items)

