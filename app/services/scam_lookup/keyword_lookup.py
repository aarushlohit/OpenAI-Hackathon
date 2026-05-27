from pydantic import BaseModel, Field


class ScamLookupResult(BaseModel):
    indicators: list[str] = Field(default_factory=list)


class ScamLookupService:
    scam_terms = {
        "security deposit": "security_deposit_request",
        "refundable deposit": "refundable_deposit_request",
        "processing fee": "processing_fee_request",
        "telegram": "telegram_channel_dependency",
        "no interview": "interview_bypass_claim",
        "direct offer": "interview_bypass_claim",
    }

    async def correlate(self, text: str) -> ScamLookupResult:
        lowered = text.lower()
        indicators = sorted({label for term, label in self.scam_terms.items() if term in lowered})
        return ScamLookupResult(indicators=indicators)

