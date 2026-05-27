from app.graph.projections import ThreatGraphProjection
from app.memory.entity_index import EntityIndex


class ThreatMemory:
    def __init__(self, entity_index: EntityIndex) -> None:
        self._entity_index = entity_index
        self._history: list[ThreatGraphProjection] = []

    async def remember(self, projection: ThreatGraphProjection) -> None:
        self._history.append(projection)
        await self._entity_index.add_projection(projection)

    async def related_to(self, entity: str) -> list[str]:
        return await self._entity_index.lookup(entity)

    async def all(self) -> list[ThreatGraphProjection]:
        return list(self._history)
