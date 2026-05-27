from pydantic import BaseModel, Field

from app.reporting.narrative_projection import NarrativeProjection


class ExecutiveReport(BaseModel):
    title: str
    audience: str = "campus safety and placement teams"
    summary: str = Field(min_length=1)
    risk_trends: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ExecutiveReportBuilder:
    def build(self, narratives: list[NarrativeProjection]) -> ExecutiveReport:
        summary = "No high-risk investigations were selected." if not narratives else narratives[0].summary
        return ExecutiveReport(
            title="Hermes-X Campaign Intelligence Summary",
            summary=summary,
            risk_trends=[narrative.headline for narrative in narratives],
            recommendations=[
                "Preserve original artifacts for review.",
                "Warn students before payment or Telegram-only onboarding.",
            ],
        )

