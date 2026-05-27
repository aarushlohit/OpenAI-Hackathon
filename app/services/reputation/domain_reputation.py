from pydantic import BaseModel, Field


class ReputationSignal(BaseModel):
    score: int = Field(ge=0, le=100)
    indicators: list[str] = Field(default_factory=list)


class DomainReputationService:
    suspicious_tlds = {".top", ".xyz", ".click", ".work", ".info", ".support"}
    trusted_job_domains = {"linkedin.com", "indeed.com", "naukri.com", "glassdoor.com"}

    async def evaluate(self, domain: str | None, source_text: str) -> ReputationSignal:
        indicators: list[str] = []
        score = 75
        lowered = source_text.lower()

        if domain:
            if any(domain.endswith(tld) for tld in self.suspicious_tlds):
                indicators.append("suspicious_tld")
                score -= 25
            if domain not in self.trusted_job_domains and "careers" not in domain:
                indicators.append("unverified_recruitment_domain")
                score -= 10
        if "telegram" in lowered and ("interview" in lowered or "onboarding" in lowered):
            indicators.append("telegram_only_onboarding_signal")
            score -= 20
        if "refundable" in lowered and any(term in lowered for term in ("deposit", "fee", "payment")):
            indicators.append("refundable_deposit_language")
            score -= 30

        return ReputationSignal(score=max(score, 0), indicators=indicators)

