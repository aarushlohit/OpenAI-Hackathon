from abc import ABC, abstractmethod

from app.graph.projections import ThreatGraphProjection


class GraphRepository(ABC):
    @abstractmethod
    async def save_projection(self, projection: ThreatGraphProjection) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_projection(self, investigation_id: str) -> ThreatGraphProjection | None:
        raise NotImplementedError

    @abstractmethod
    async def all_projections(self) -> list[ThreatGraphProjection]:
        raise NotImplementedError


class InMemoryGraphRepository(GraphRepository):
    def __init__(self) -> None:
        self._projections: dict[str, ThreatGraphProjection] = {}

    async def save_projection(self, projection: ThreatGraphProjection) -> None:
        self._projections[projection.investigation_id] = projection

    async def get_projection(self, investigation_id: str) -> ThreatGraphProjection | None:
        return self._projections.get(investigation_id)

    async def all_projections(self) -> list[ThreatGraphProjection]:
        return list(self._projections.values())

