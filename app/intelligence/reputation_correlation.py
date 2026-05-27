from pydantic import BaseModel, Field

from app.models.investigation_context import InvestigationContext


class CorrelationResult(BaseModel):
    indicators: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)


class ReputationCorrelationEngine:
    async def correlate(self, context: InvestigationContext) -> CorrelationResult:
        indicators: list[str] = []
        if context.entities.telegram_handles and context.entities.upi_ids:
            indicators.append("telegram_payment_correlation")
        if context.entities.domains and any(domain.endswith(".xyz") for domain in context.entities.domains):
            indicators.append("suspicious_domain_correlation")
        if len(context.entities.urls) > 1:
            indicators.append("multi_url_campaign_hint")
        confidence = min(0.9, 0.3 + (0.15 * len(indicators)))
        return CorrelationResult(indicators=sorted(set(indicators)), confidence=confidence)

