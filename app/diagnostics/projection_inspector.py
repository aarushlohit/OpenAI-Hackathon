from app.graph.projections import ThreatGraphProjection


class ProjectionInspector:
    def inspect(self, projection: ThreatGraphProjection) -> dict[str, int]:
        return {"nodes": len(projection.nodes), "edges": len(projection.edges)}

