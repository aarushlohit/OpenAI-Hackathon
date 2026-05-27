from app.graph.projections import ThreatGraphProjection


class GraphIntegrityInspector:
    def inspect(self, projection: ThreatGraphProjection) -> bool:
        node_ids = {node.id for node in projection.nodes}
        return all(edge.source in node_ids and edge.target in node_ids for edge in projection.edges)

