from __future__ import annotations

import sys

from app.agents.base import AgentContext, InvestigationAgent
from app.models.osint_result import OSINTIndicator, OSINTResult
from app.providers.nvidia_reasoning_client import NVIDIA_MODEL, NvidiaReasoningClient
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationRequest
from app.security.model_output_validator import ModelOutputValidator
from app.services.reputation import DomainReputationService
from app.services.scam_lookup import ScamLookupService
from app.services.whois import WhoisService


def _console_log(message: str) -> None:
    print(f"[OSINT] {message}", file=sys.stderr, flush=True)


_OSINT_SYSTEM_PROMPT = (
    "You are a cybersecurity OSINT analyst. Return compact JSON only. No markdown. "
    "Analyze recruitment infrastructure risk: domains, handles, Telegram, payment routes, "
    "brand impersonation, phishing, and suspicious onboarding."
)


class OSINTAgent(InvestigationAgent):
    name = "osint"

    def __init__(
        self,
        whois_service: WhoisService,
        reputation_service: DomainReputationService,
        scam_lookup_service: ScamLookupService,
        prompt_registry: PromptRegistry,
        nvidia_client: NvidiaReasoningClient | None = None,
    ) -> None:
        self._whois_service = whois_service
        self._reputation_service = reputation_service
        self._scam_lookup_service = scam_lookup_service
        self._prompt_registry = prompt_registry
        self._nvidia_client = nvidia_client
        self._validator = ModelOutputValidator()

    async def run(self, request: InvestigationRequest, context: AgentContext) -> OSINTResult:
        await context.log(request, self.name, "Starting OSINT analysis")

        deterministic_result = await self._get_deterministic_data(request, context)

        if self._nvidia_client is None:
            raise RuntimeError("NVIDIA runtime unavailable. Investigation aborted.")

        _console_log("NVIDIA cognition started...")
        _console_log(f"Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")

        user_prompt = (
            f"EVIDENCE:\n{request.raw_input}\n\n"
            "VALIDATOR CONTEXT:\n"
            f"- domain_age_days: {deterministic_result.domain_age_days or 'N/A'}\n"
            f"- ssl_valid: {deterministic_result.ssl_valid}\n"
            f"- deterministic_indicators: {', '.join(deterministic_result.suspicious_indicators) or 'none'}\n\n"
            "Return this JSON with real values. Limit to 3 indicators. Evidence under 100 chars: "
            '{"reputation_score":0-100,"confidence":0.0-1.0,'
            '"indicators":[{"name":"...","severity":"LOW|MEDIUM|HIGH|CRITICAL",'
            '"confidence":0.0-1.0,"evidence":"...","source":"ai_reasoned"}],'
            '"summary":"...","recommended_action":"...","reasoning_type":"osint_analysis"}'
        )

        ai_output, latency_ms = await self._nvidia_client.analyze_text(
            system_prompt=_OSINT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.15,
            max_tokens=1200,
        )
        _console_log(f"Response received ({latency_ms}ms)")

        validated = self._validator.validate_osint_output(ai_output)
        ai_indicators = [
            OSINTIndicator(
                name=ind.get("name", "unknown"),
                severity=ind.get("severity", "medium"),
                confidence=min(1.0, max(0.0, float(ind.get("confidence", 0.5)))),
                evidence=ind.get("evidence", "")[:1000],
                source=ind.get("source", "ai_reasoned"),
            )
            for ind in validated.get("indicators", [])
        ]

        all_indicators = sorted(set(deterministic_result.suspicious_indicators + [i.name for i in ai_indicators]))
        reputation_score = min(100, max(0, int(validated.get("reputation_score", deterministic_result.reputation_score))))
        confidence = min(1.0, max(0.0, float(validated.get("confidence", deterministic_result.confidence))))
        metadata = self._nvidia_client.last_metadata
        provider = metadata.provider if metadata else "nvidia_nim"
        model = metadata.model if metadata else NVIDIA_MODEL

        _console_log("Infrastructure cognition complete")
        _console_log(f"Reputation Score: {reputation_score}/100")
        _console_log(f"Confidence: {confidence:.0%}")
        _console_log(f"Indicators Detected: {len(ai_indicators)}")

        result = OSINTResult(
            investigation_id=request.investigation_id,
            domain_age_days=deterministic_result.domain_age_days,
            ssl_valid=deterministic_result.ssl_valid,
            reputation_score=reputation_score,
            suspicious_indicators=all_indicators,
            confidence=confidence,
            provider=provider,
            provider_model=model,
            reasoning_type="osint_analysis",
            ai_indicators=ai_indicators,
            summary=validated.get("summary", "")[:500],
        )
        await context.log(
            request, self.name,
            f"OSINT analysis complete: reputation={reputation_score}, indicators={len(ai_indicators)}, provider={provider}"
        )
        return result

    async def _get_deterministic_data(self, request: InvestigationRequest, context: AgentContext) -> OSINTResult:
        self._prompt_registry.load("osint", "system_prompt")
        profile = await self._whois_service.inspect(request.raw_input)
        reputation = await self._reputation_service.evaluate(profile.domain, request.raw_input)
        scam_lookup = await self._scam_lookup_service.correlate(request.raw_input)
        indicators = sorted(set(reputation.indicators + scam_lookup.indicators))
        confidence = 0.45 + min(len(indicators) * 0.1, 0.4)
        if profile.domain_age_days is not None and profile.domain_age_days <= 30:
            indicators.append("newly_registered_domain")
            confidence = min(confidence + 0.1, 0.95)
        return OSINTResult(
            investigation_id=request.investigation_id,
            domain_age_days=profile.domain_age_days,
            ssl_valid=profile.ssl_valid,
            reputation_score=reputation.score,
            suspicious_indicators=indicators,
            confidence=min(confidence, 0.95),
            provider="deterministic",
            provider_model="whois+reputation+scam_lookup",
            reasoning_type="deterministic",
            ai_indicators=[],
            summary=f"OSINT analysis: {len(indicators)} indicator(s) detected via deterministic services.",
        )
