from pydantic import BaseModel, Field

from app.graph.projections import ThreatGraphProjection, ThreatNodeKind


class CampaignDetection(BaseModel):
    campaign_id: str
    indicators: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    severity: str


class CampaignDetector:
    async def detect(self, projections: list[ThreatGraphProjection]) -> list[CampaignDetection]:
        detections: list[CampaignDetection] = []
        payment_map = self._index_by_kind(projections, ThreatNodeKind.UPI)
        domain_map = self._index_by_kind(projections, ThreatNodeKind.DOMAIN)
        detections.extend(self._detections(payment_map, "reused_payment_method", "high"))
        detections.extend(self._detections(domain_map, "reused_domain_cluster", "medium"))
        return detections

    def _index_by_kind(
        self,
        projections: list[ThreatGraphProjection],
        kind: ThreatNodeKind,
    ) -> dict[str, set[str]]:
        index: dict[str, set[str]] = {}
        for projection in projections:
            for node in projection.nodes:
                if node.kind == kind:
                    index.setdefault(node.id, set()).add(projection.investigation_id)
        return index

    def _detections(
        self,
        index: dict[str, set[str]],
        indicator: str,
        severity: str,
    ) -> list[CampaignDetection]:
        detections: list[CampaignDetection] = []
        for entity, investigations in index.items():
            if len(investigations) >= 2:
                detections.append(
                    CampaignDetection(
                        campaign_id=f"CMP-{abs(hash(entity)) % 1_000_000:06d}",
                        indicators=[indicator, entity, *sorted(investigations)],
                        confidence=min(0.95, 0.55 + (0.1 * len(investigations))),
                        severity=severity,
                    )
                )
        return detections

