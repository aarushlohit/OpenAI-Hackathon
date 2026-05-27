from app.graph.edge_builder import GraphEdgeBuilder
from app.graph.node_builder import GraphNodeBuilder
from app.graph.projections import ThreatGraphProjection
from app.graph.repositories import GraphRepository
from app.models.investigation_context import InvestigationContext


class ThreatGraphEngine:
    def __init__(
        self,
        repository: GraphRepository,
        node_builder: GraphNodeBuilder | None = None,
        edge_builder: GraphEdgeBuilder | None = None,
    ) -> None:
        self._repository = repository
        self._node_builder = node_builder or GraphNodeBuilder()
        self._edge_builder = edge_builder or GraphEdgeBuilder()

    async def project(self, context: InvestigationContext) -> ThreatGraphProjection:
        nodes = self._node_builder.build(context)
        edges = self._edge_builder.build(context.investigation_id, nodes)
        projection = ThreatGraphProjection(
            investigation_id=context.investigation_id,
            nodes=nodes,
            edges=edges,
        )
        await self._repository.save_projection(projection)
        return projection

