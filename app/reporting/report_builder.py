from pydantic import BaseModel, Field

from app.models.investigation_context import InvestigationContext
from app.models.threat_score import ThreatScore
from app.schemas.investigation import EvidenceItem


class InvestigationReport(BaseModel):
    investigation_id: str
    severity: str
    score: int = Field(ge=0, le=100)
    summary: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    entities: dict[str, list[str]] = Field(default_factory=dict)


class ReportBuilder:
    def build(
        self,
        context: InvestigationContext,
        threat_score: ThreatScore,
        evidence: list[EvidenceItem],
    ) -> InvestigationReport:
        return InvestigationReport(
            investigation_id=context.investigation_id,
            severity=threat_score.severity.value,
            score=threat_score.final_score,
            summary=threat_score.explanation,
            evidence=evidence,
            entities=context.entities.model_dump(),
        )

    def export_snapshot(
        self,
        context: InvestigationContext,
        threat_score: ThreatScore,
        evidence: list[EvidenceItem],
    ) -> dict:
        report = self.build(context, threat_score, evidence)
        return report.model_dump(mode="json")
