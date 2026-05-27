from app.graph.projections import ThreatEdgeKind, ThreatGraphNode, ThreatNodeKind


class RelationshipRules:
    def relation_for(self, node: ThreatGraphNode) -> ThreatEdgeKind:
        if node.kind in {ThreatNodeKind.UPI, ThreatNodeKind.PAYMENT_WALLET}:
            return ThreatEdgeKind.SHARES_PAYMENT_METHOD
        if node.kind == ThreatNodeKind.DOMAIN:
            return ThreatEdgeKind.SHARES_DOMAIN_PATTERN
        if node.kind == ThreatNodeKind.OFFER_SIGNATURE:
            return ThreatEdgeKind.SHARES_SIGNATURE
        return ThreatEdgeKind.LINKED_TO

