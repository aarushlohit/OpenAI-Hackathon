from app.graph.projections import ThreatGraphProjection


class EntityIndex:
    def __init__(self) -> None:
        self._index: dict[str, set[str]] = {}

    async def add_projection(self, projection: ThreatGraphProjection) -> None:
        for node in projection.nodes:
            if node.id != projection.investigation_id:
                self._index.setdefault(node.id, set()).add(projection.investigation_id)

    async def lookup(self, entity: str) -> list[str]:
        return sorted(self._index.get(entity, set()))

