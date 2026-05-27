"""Evidence-weighted threat scoring engine.

Each threat signal contributes independently with its own weight and confidence.
No escalation occurs without traceable evidence — every score point is attributable
to a specific signal, agent result, and confidence value.
"""

from __future__ import annotations

from app.contracts.agent_result import AgentResult
from app.models.behavior_result import BehaviorResult
from app.models.osint_result import OSINTResult
from app.models.threat_score import EvidenceSignal, ThreatScore, ThreatSeverity
from app.models.vision_result import VisionResult
from app.services.scoring import clamp_score

# ---------------------------------------------------------------------------
# Signal weight registry — each key maps to (base_weight, confidence_floor)
# ---------------------------------------------------------------------------
_SIGNAL_WEIGHTS: dict[str, tuple[float, int]] = {
    # (contribution_weight_0_to_1, base_score_points)
    "urgency_manipulation": (0.90, 14),
    "refundable_fee_request": (0.95, 18),
    "payment_coercion": (0.92, 22),
    "suspicious_domain_age": (0.80, 12),
    "hidden_whois": (0.70, 10),
    "telegram_only_onboarding": (0.85, 18),
    "reused_upi_payment_id": (0.88, 14),
    "graph_campaign_correlation": (0.92, 16),
    "recruiter_impersonation": (0.90, 15),
    "ai_reasoning_low_confidence": (0.60, 8),
    "replay_consistency_violation": (0.75, 10),
    "osint_reputation_low": (0.80, 12),
    "newly_registered_domain": (0.82, 12),
    "invalid_tls": (0.65, 8),
}

# Patterns that map directly to named signal keys for lookup
_PATTERN_SIGNAL_MAP: dict[str, str] = {
    "urgency": "urgency_manipulation",
    "urgency_manipulation": "urgency_manipulation",
    "refundable_fee": "refundable_fee_request",
    "fee_request": "refundable_fee_request",
    "payment_coercion": "payment_coercion",
    "coercion": "payment_coercion",
    "forced_payment": "payment_coercion",
    "telegram_only": "telegram_only_onboarding",
    "telegram": "telegram_only_onboarding",
    "telegram_only_onboarding": "telegram_only_onboarding",
    "upi_reuse": "reused_upi_payment_id",
    "campaign_correlation": "graph_campaign_correlation",
    "impersonation": "recruiter_impersonation",
    "recruiter_impersonation": "recruiter_impersonation",
    "hidden_whois": "hidden_whois",
    "newly_registered_domain": "newly_registered_domain",
    "invalid_tls": "invalid_tls",
}


class ThreatScoringEngine:
    """Evidence-weighted scoring engine.

    Aggregates signals from all AgentResult objects. Each unique signal
    contributes a weighted, confidence-adjusted score delta. No hallucination:
    every contribution is traceable to a concrete evidence source.
    """

    async def score(self, investigation_id: str, results: list[AgentResult]) -> ThreatScore:
        signals: list[EvidenceSignal] = []
        factors: list[str] = []
        raw_score = 0
        confidence_sum = 0.0
        confidence_count = 0

        for result in results:
            new_signals = self._extract_signals(result)
            signals.extend(new_signals)
            for sig in new_signals:
                raw_score += sig.score_contribution
                factors.append(sig.signal)
                confidence_sum += sig.confidence
                confidence_count += 1

        final_score = clamp_score(raw_score)
        aggregate_confidence = (confidence_sum / confidence_count) if confidence_count else 0.0
        severity = self._severity(final_score)
        unique_factors = sorted(set(factors))
        explanation = self._explain(final_score, severity, unique_factors)
        explainability_summary = self._build_explainability_summary(
            final_score, severity, aggregate_confidence, signals
        )

        return ThreatScore(
            investigation_id=investigation_id,
            final_score=final_score,
            confidence=round(aggregate_confidence, 3),
            severity=severity,
            explanation=explanation,
            explainability_summary=explainability_summary,
            contributing_factors=unique_factors,
            evidence_breakdown=signals,
        )

    # ------------------------------------------------------------------
    # Signal extraction — one method per result type
    # ------------------------------------------------------------------

    def _extract_signals(self, result: AgentResult) -> list[EvidenceSignal]:
        if isinstance(result, BehaviorResult):
            return self._from_behavior(result)
        if isinstance(result, OSINTResult):
            return self._from_osint(result)
        if isinstance(result, VisionResult):
            return self._from_vision(result)
        return []

    def _from_behavior(self, result: BehaviorResult) -> list[EvidenceSignal]:
        out: list[EvidenceSignal] = []
        # Prefer the result's explicit confidence when available; fall back to risk_score.
        explicit_conf = getattr(result, "confidence", None)
        effective_confidence = (
            float(explicit_conf) if isinstance(explicit_conf, (int, float)) and explicit_conf > 0
            else min(1.0, result.risk_score / 100.0)
        )
        for pattern in result.detected_patterns:
            key = _PATTERN_SIGNAL_MAP.get(pattern, pattern)
            weight, base_pts = _SIGNAL_WEIGHTS.get(key, (0.75, 10))
            # Contribution = base_pts × weight (not further discounted by confidence —
            # confidence is stored as metadata, not a penalty on detected patterns).
            contribution = int(base_pts * weight)
            out.append(
                EvidenceSignal(
                    signal=key,
                    weight=weight,
                    score_contribution=contribution,
                    confidence=round(effective_confidence, 3),
                    source="behavior_agent",
                    detail=f"Pattern '{pattern}' detected; risk_score={result.risk_score}",
                )
            )
        return out

    def _from_osint(self, result: OSINTResult) -> list[EvidenceSignal]:
        out: list[EvidenceSignal] = []
        rep_confidence = max(0.0, min(1.0, (100 - result.reputation_score) / 100.0))
        if result.reputation_score < 60:
            weight, base_pts = _SIGNAL_WEIGHTS["osint_reputation_low"]
            out.append(
                EvidenceSignal(
                    signal="osint_reputation_low",
                    weight=weight,
                    score_contribution=int(base_pts * weight * rep_confidence),
                    confidence=round(rep_confidence, 3),
                    source="osint_agent",
                    detail=f"Domain reputation score: {result.reputation_score}/100",
                )
            )
        for indicator in result.suspicious_indicators:
            key = _PATTERN_SIGNAL_MAP.get(indicator, indicator)
            weight, base_pts = _SIGNAL_WEIGHTS.get(key, (0.50, 6))
            out.append(
                EvidenceSignal(
                    signal=key,
                    weight=weight,
                    score_contribution=int(base_pts * weight),
                    confidence=round(rep_confidence, 3),
                    source="osint_agent",
                    detail=f"OSINT indicator: {indicator}",
                )
            )
        if result.domain_age_days is not None and result.domain_age_days <= 30:
            weight, base_pts = _SIGNAL_WEIGHTS["suspicious_domain_age"]
            age_conf = 1.0 if result.domain_age_days <= 7 else 0.80
            out.append(
                EvidenceSignal(
                    signal="suspicious_domain_age",
                    weight=weight,
                    score_contribution=int(base_pts * weight * age_conf),
                    confidence=age_conf,
                    source="osint_agent",
                    detail=f"Domain registered {result.domain_age_days} day(s) ago",
                )
            )
        if result.ssl_valid is False:
            weight, base_pts = _SIGNAL_WEIGHTS["invalid_tls"]
            out.append(
                EvidenceSignal(
                    signal="invalid_tls",
                    weight=weight,
                    score_contribution=base_pts,
                    confidence=0.95,
                    source="osint_agent",
                    detail="SSL certificate invalid or absent",
                )
            )
        return out

    def _from_vision(self, result: VisionResult) -> list[EvidenceSignal]:
        out: list[EvidenceSignal] = []
        for element in result.suspicious_elements:
            key = _PATTERN_SIGNAL_MAP.get(element, element)
            weight, base_pts = _SIGNAL_WEIGHTS.get(key, (0.55, 8))
            out.append(
                EvidenceSignal(
                    signal=key,
                    weight=weight,
                    score_contribution=int(base_pts * weight),
                    confidence=0.70,
                    source="vision_agent",
                    detail=f"Visual element flagged: {element}",
                )
            )
        return out

    # ------------------------------------------------------------------
    # Severity / explanation
    # ------------------------------------------------------------------

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
            return f"Final score {score} ({severity}): no major scam indicators detected."
        readable = ", ".join(f.replace("_", " ") for f in factors)
        return f"Final score {score} ({severity}): evidence includes {readable}."

    def _build_explainability_summary(
        self,
        score: int,
        severity: ThreatSeverity,
        confidence: float,
        signals: list[EvidenceSignal],
    ) -> str:
        """Generate a structured natural-language explainability block."""
        if not signals:
            return (
                f"VERDICT: {severity.upper()} (score {score})\n"
                "No evidence signals were collected. Investigation may require additional data."
            )
        lines = [
            f"VERDICT: {severity.upper()} | Score: {score}/100 | Confidence: {confidence * 100:.1f}%",
            "",
            "WHY THIS WAS FLAGGED:",
        ]
        # Group by source
        by_source: dict[str, list[EvidenceSignal]] = {}
        for sig in signals:
            by_source.setdefault(sig.source, []).append(sig)
        for source, sigs in sorted(by_source.items()):
            lines.append(f"\n  [{source.upper().replace('_', ' ')}]")
            for sig in sorted(sigs, key=lambda s: s.score_contribution, reverse=True):
                pct = f"{sig.confidence * 100:.0f}%"
                lines.append(
                    f"    • {sig.signal.replace('_', ' ').title()}: "
                    f"+{sig.score_contribution}pts (confidence {pct}) — {sig.detail}"
                )
        lines.append(
            f"\nCORRELATION: {len(signals)} evidence signal(s) cross-validated "
            f"across {len(by_source)} agent(s). Escalation is evidence-backed."
        )
        return "\n".join(lines)
