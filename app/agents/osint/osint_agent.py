from app.agents.base import AgentContext, InvestigationAgent
from app.models.osint_result import OSINTResult
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationRequest
from app.services.reputation import DomainReputationService
from app.services.scam_lookup import ScamLookupService
from app.services.whois import WhoisService


class OSINTAgent(InvestigationAgent):
    name = "osint"

    def __init__(
        self,
        whois_service: WhoisService,
        reputation_service: DomainReputationService,
        scam_lookup_service: ScamLookupService,
        prompt_registry: PromptRegistry,
    ) -> None:
        self._whois_service = whois_service
        self._reputation_service = reputation_service
        self._scam_lookup_service = scam_lookup_service
        self._prompt_registry = prompt_registry

    async def run(self, request: InvestigationRequest, context: AgentContext) -> OSINTResult:
        await context.log(request, self.name, "Checking domain and public scam indicators")
        self._prompt_registry.load("osint", "system_prompt")
        profile = await self._whois_service.inspect(request.raw_input)
        reputation = await self._reputation_service.evaluate(profile.domain, request.raw_input)
        scam_lookup = await self._scam_lookup_service.correlate(request.raw_input)
        indicators = sorted(set(reputation.indicators + scam_lookup.indicators))
        confidence = 0.45 + min(len(indicators) * 0.1, 0.4)
        if profile.domain_age_days is not None and profile.domain_age_days <= 30:
            indicators.append("newly_registered_domain")
            confidence = min(confidence + 0.1, 0.95)
        await context.log(request, self.name, f"Correlated {len(indicators)} OSINT indicator(s)")
        return OSINTResult(
            investigation_id=request.investigation_id,
            domain_age_days=profile.domain_age_days,
            ssl_valid=profile.ssl_valid,
            reputation_score=reputation.score,
            suspicious_indicators=indicators,
            confidence=min(confidence, 0.95),
        )

