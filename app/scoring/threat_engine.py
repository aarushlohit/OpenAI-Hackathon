from app.contracts.agent_result import AgentResult
from app.models.behavior_result import BehaviorResult
from app.models.osint_result import OSINTResult
from app.models.threat_score import ThreatScore, ThreatSeverity
from app.models.vision_result import VisionResult
from app.services.scoring import clamp_score


class ThreatScoringEngine:
    async def score(self, investigation_id: str, results: list[AgentResult]) -> ThreatScore:
        factors: list[str] = []
        score = 0

        for result in results:
            if isinstance(result, BehaviorResult):
                score += int(result.risk_score * 0.45)
                factors.extend(result.detected_patterns)
            elif isinstance(result, OSINTResult):
                score += int((100 - result.reputation_score) * 0.35)
                factors.extend(result.suspicious_indicators)
                if result.domain_age_days is not None and result.domain_age_days <= 30:
                    score += 12
                    factors.append("newly_registered_domain")
                if result.ssl_valid is False:
                    score += 8
                    factors.append("invalid_tls")
            elif isinstance(result, VisionResult):
                score += len(result.suspicious_elements) * 8
                factors.extend(result.suspicious_elements)

        final_score = clamp_score(score)
        severity = self._severity(final_score)
        unique_factors = sorted(set(factors))
        explanation = self._explain(final_score, severity, unique_factors)
        return ThreatScore(
            investigation_id=investigation_id,
            final_score=final_score,
            severity=severity,
            explanation=explanation,
            contributing_factors=unique_factors,
        )

    def _severity(self, score: int) -> ThreatSeverity:
        if score >= 85:
            return ThreatSeverity.CRITICAL
        if score >= 65:
            return ThreatSeverity.HIGH
        if score >= 35:
            return ThreatSeverity.MEDIUM
        return ThreatSeverity.LOW

    def _explain(self, score: int, severity: ThreatSeverity, factors: list[str]) -> str:
        if not factors:
            return f"Final score {score} is {severity}; no major scam indicators were found."
        readable = ", ".join(factor.replace("_", " ") for factor in factors)
        return f"Final score {score} is {severity}; contributing evidence includes {readable}."

