from app.graph.projections import ThreatGraphEdge, ThreatGraphNode
from app.graph.relationship_rules import RelationshipRules


class GraphEdgeBuilder:
    def __init__(self, rules: RelationshipRules | None = None) -> None:
        self._rules = rules or RelationshipRules()

    def build(self, investigation_id: str, nodes: list[ThreatGraphNode]) -> list[ThreatGraphEdge]:
        edges: list[ThreatGraphEdge] = []
        for node in nodes:
            if node.id == investigation_id:
                continue
            edges.append(
                ThreatGraphEdge(
                    source=investigation_id,
                    target=node.id,
                    kind=self._rules.relation_for(node),
                    confidence=0.75,
                )
            )
        return edges

