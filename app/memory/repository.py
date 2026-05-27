from abc import ABC, abstractmethod
from uuid import UUID

from app.memory.models import MemoryRecord


class MemoryRepository(ABC):
    @abstractmethod
    async def append(self, record: MemoryRecord) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_correlation(self, correlation_id: UUID) -> list[MemoryRecord]:
        raise NotImplementedError


class InMemoryMemoryRepository(MemoryRepository):
    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    async def append(self, record: MemoryRecord) -> None:
        self._records.append(record)

    async def list_by_correlation(self, correlation_id: UUID) -> list[MemoryRecord]:
        return [record for record in self._records if record.correlation_id == correlation_id]

