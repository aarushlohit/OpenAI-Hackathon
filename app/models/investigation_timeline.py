from datetime import UTC, datetime

from pydantic import BaseModel, Field


class TimelineEntry(BaseModel):
    offset_ms: int = Field(ge=0)
    event: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=2_000)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InvestigationTimeline(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    entries: list[TimelineEntry] = Field(default_factory=list)

    def append(self, entry: TimelineEntry) -> None:
        self.entries.append(entry)

