from app.models.investigation_context import InvestigationContext
from app.models.threat_score import ThreatScore
from app.reporting.narrative_projection import NarrativeProjection


class StoryBuilder:
    def build(self, context: InvestigationContext, threat_score: ThreatScore) -> NarrativeProjection:
        entities = context.entities
        points: list[str] = []
        if entities.domains:
            points.append(f"Domain evidence included {', '.join(entities.domains)}.")
        if entities.telegram_handles:
            points.append(f"Telegram handles appeared: {', '.join(entities.telegram_handles)}.")
        if entities.upi_ids:
            points.append(f"Payment identifiers appeared: {', '.join(entities.upi_ids)}.")
        return NarrativeProjection(
            investigation_id=context.investigation_id,
            headline=f"{threat_score.severity.value.upper()} recruitment fraud risk",
            summary=threat_score.explanation,
            key_points=points,
        )

