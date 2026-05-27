from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MemoryRecord(BaseModel):
    memory_id: UUID = Field(default_factory=uuid4)
    correlation_id: UUID
    namespace: str = Field(min_length=1, max_length=80)
    key: str = Field(min_length=1, max_length=160)
    value: dict
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

