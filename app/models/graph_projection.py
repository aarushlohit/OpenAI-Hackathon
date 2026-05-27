from enum import StrEnum

from pydantic import BaseModel, Field

from app.models.investigation_context import InvestigationContext


class GraphNodeKind(StrEnum):
    DOMAIN = "domain"
    EMAIL = "email"
    TELEGRAM = "telegram"
    UPI = "upi"
    INVESTIGATION = "investigation"


class GraphNode(BaseModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    kind: GraphNodeKind


class GraphEdge(BaseModel):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    relation: str = Field(min_length=1)


class GraphProjection(BaseModel):
    investigation_id: str
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class GraphProjectionBuilder:
    def build(self, context: InvestigationContext) -> GraphProjection:
        root = GraphNode(
            id=context.investigation_id,
            label=context.investigation_id,
            kind=GraphNodeKind.INVESTIGATION,
        )
        nodes = [root]
        nodes += [GraphNode(id=value, label=value, kind=GraphNodeKind.DOMAIN) for value in context.entities.domains]
        nodes += [GraphNode(id=value, label=value, kind=GraphNodeKind.EMAIL) for value in context.entities.emails]
        nodes += [GraphNode(id=value, label=f"@{value}", kind=GraphNodeKind.TELEGRAM) for value in context.entities.telegram_handles]
        nodes += [GraphNode(id=value, label=value, kind=GraphNodeKind.UPI) for value in context.entities.upi_ids]
        edges = [
            GraphEdge(source=context.investigation_id, target=node.id, relation="contains")
            for node in nodes
            if node.id != context.investigation_id
        ]
        return GraphProjection(investigation_id=context.investigation_id, nodes=nodes, edges=edges)

