from pydantic import BaseModel, Field

from app.graph.projections import ThreatGraphProjection
from app.graph.repositories import GraphRepository
from app.intelligence.campaign_detector import CampaignDetection, CampaignDetector


class CorrelationSummary(BaseModel):
    investigation_id: str
    related_investigations: list[str] = Field(default_factory=list)
    campaign_detections: list[CampaignDetection] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ThreatCorrelationEngine:
    def __init__(self, repository: GraphRepository, campaign_detector: CampaignDetector) -> None:
        self._repository = repository
        self._campaign_detector = campaign_detector

    async def correlate(self, projection: ThreatGraphProjection) -> CorrelationSummary:
        projections = await self._repository.all_projections()
        related = self._related_investigations(projection, projections)
        campaigns = await self._campaign_detector.detect(projections)
        confidence = min(0.95, 0.35 + (0.1 * len(related)) + (0.15 * len(campaigns)))
        return CorrelationSummary(
            investigation_id=projection.investigation_id,
            related_investigations=related,
            campaign_detections=campaigns,
            confidence=confidence,
        )

    def _related_investigations(
        self,
        target: ThreatGraphProjection,
        projections: list[ThreatGraphProjection],
    ) -> list[str]:
        target_entities = {node.id for node in target.nodes if node.id != target.investigation_id}
        related: set[str] = set()
        for projection in projections:
            if projection.investigation_id == target.investigation_id:
                continue
            other_entities = {node.id for node in projection.nodes if node.id != projection.investigation_id}
            if target_entities & other_entities:
                related.add(projection.investigation_id)
        return sorted(related)

