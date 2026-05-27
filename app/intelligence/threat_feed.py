from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ThreatFeedItem(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    detail: str = Field(min_length=1, max_length=1_000)
    severity: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ThreatFeed:
    def __init__(self) -> None:
        self._items: list[ThreatFeedItem] = []

    async def publish(self, item: ThreatFeedItem) -> None:
        self._items.append(item)

    async def latest(self, limit: int = 25) -> list[ThreatFeedItem]:
        return list(reversed(self._items[-limit:]))

