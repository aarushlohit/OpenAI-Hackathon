from app.graph.projections import ThreatGraphNode, ThreatNodeKind
from app.models.investigation_context import InvestigationContext


class GraphNodeBuilder:
    def build(self, context: InvestigationContext) -> list[ThreatGraphNode]:
        nodes = [
            ThreatGraphNode(
                id=context.investigation_id,
                label=context.investigation_id,
                kind=ThreatNodeKind.INVESTIGATION,
            )
        ]
        entities = context.entities
        nodes.extend(self._nodes(entities.domains, ThreatNodeKind.DOMAIN))
        nodes.extend(self._nodes(entities.emails, ThreatNodeKind.EMAIL))
        nodes.extend(self._nodes(entities.telegram_handles, ThreatNodeKind.TELEGRAM, prefix="@"))
        nodes.extend(self._nodes(entities.upi_ids, ThreatNodeKind.UPI))
        return nodes

    def _nodes(
        self,
        values: list[str],
        kind: ThreatNodeKind,
        prefix: str = "",
    ) -> list[ThreatGraphNode]:
        return [ThreatGraphNode(id=value, label=f"{prefix}{value}", kind=kind) for value in values]

