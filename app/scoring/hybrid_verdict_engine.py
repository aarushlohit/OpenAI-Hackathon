"""Hybrid verdict engine combining AI reasoning + deterministic validation + cross-agent consensus.

This engine produces trustworthy verdicts through:
1. AI reasoning from multiple specialized agents
2. Deterministic validation layer (pattern matching, domain checks, etc.)
3. Cross-agent consensus and correlation
4. Web verification trust signals (can reduce score for legitimate companies)
5. Explainability and transparency
"""

import logging
from dataclasses import dataclass

from app.contracts.agent_result import AgentResult
from app.models.audio_result import AudioResult
from app.models.behavior_result import BehaviorResult
from app.models.osint_result import OSINTResult
from app.models.threat_score import EvidenceSignal, ThreatScore, ThreatSeverity
from app.models.vision_result import VisionResult
from app.models.web_search_result import WebSearchResult
from app.services.scoring import clamp_score

logger = logging.getLogger(__name__)


@dataclass
class VerdictComponent:
    """A single component of the final verdict."""

    component_type: str  # "ai_reasoning" | "deterministic_validation" | "consensus"
    provider: str
    model: str | None
    signals: list[EvidenceSignal]
    confidence: float
    reasoning_trace: str


class HybridVerdictEngine:
    """Produces verified, explainable, and trustworthy verdicts.

    Combines:
    - AI reasoning from specialized agents (NVIDIA Nemotron)
    - Deterministic pattern validation
    - Cross-agent consensus rules
    - Provider attribution and transparency
    """

    def __init__(self) -> None:
        self._deterministic_validator = DeterministicValidator()
        self._consensus_analyzer = ConsensusAnalyzer()

    async def produce_verdict(
        self, investigation_id: str, agent_results: list[AgentResult]
    ) -> tuple[ThreatScore, list[VerdictComponent]]:
        """Produce a verified, explainable threat verdict.

        Returns:
            (threat_score, verdict_components)
        """
        # 1. Extract AI signals from all results
        ai_signals = self._extract_ai_signals(agent_results)

        # 2. Run deterministic validation layer
        deterministic_signals = await self._deterministic_validator.validate(
            investigation_id, agent_results
        )

        # 3. Analyze cross-agent consensus
        consensus_signals, consensus_strength = self._consensus_analyzer.analyze(agent_results)

        # 4. Extract web verification trust delta
        web_trust_delta = self._extract_web_trust_delta(agent_results)
        web_summary = self._extract_web_summary(agent_results)

        # 5. Combine all signals with proper weighting
        all_signals = ai_signals + deterministic_signals + consensus_signals

        # 6. Calculate final score with web trust calibration
        raw_score = self._calculate_final_score(all_signals)
        final_score = max(0, min(100, raw_score + web_trust_delta))
        aggregate_confidence = self._calculate_aggregate_confidence(all_signals)
        severity = self._determine_severity(final_score)

        # 7. Build explainability summary
        explanation, explainability_summary = self._build_explanations(
            final_score, severity, all_signals, consensus_strength, web_summary, web_trust_delta
        )

        # 8. Determine verdict source and primary cognition
        verdict_source = self._determine_verdict_source(ai_signals, deterministic_signals, consensus_signals)
        primary_cognition = "nvidia_nim" if ai_signals else "deterministic_engine"
        deterministic_confirmed = len(deterministic_signals) > 0
        consensus_reached = consensus_strength >= 0.5

        threat_score = ThreatScore(
            investigation_id=investigation_id,
            final_score=final_score,
            confidence=round(aggregate_confidence, 3),
            severity=severity,
            explanation=explanation,
            explainability_summary=explainability_summary,
            contributing_factors=self._extract_unique_factors(all_signals),
            evidence_breakdown=all_signals,
            verdict_source=verdict_source,
            primary_cognition=primary_cognition,
            deterministic_validation=deterministic_confirmed,
            cross_agent_consensus=consensus_reached,
        )

        # Build verdict components for transparency
        verdict_components: list[VerdictComponent] = []

        # AI component
        if ai_signals:
            ai_confidence = sum(s.confidence for s in ai_signals) / len(ai_signals)
            providers = set(s.source for s in ai_signals if "ai" in s.source.lower())
            verdict_components.append(
                VerdictComponent(
                    component_type="ai_reasoning",
                    provider=", ".join(providers) or "NVIDIA Nemotron Omni",
                    model="nemotron-3-nano-omni-30b-a3b-reasoning",
                    signals=ai_signals,
                    confidence=ai_confidence,
                    reasoning_trace="AI agents analyzed behavior, OSINT, vision, and audio signals",
                )
            )

        # Deterministic component
        if deterministic_signals:
            det_confidence = sum(s.confidence for s in deterministic_signals) / len(deterministic_signals)
            verdict_components.append(
                VerdictComponent(
                    component_type="deterministic_validation",
                    provider="hermes_deterministic_engine",
                    model="v1",
                    signals=deterministic_signals,
                    confidence=det_confidence,
                    reasoning_trace="Deterministic validation confirmed suspicious indicators",
                )
            )

        # Consensus component
        if consensus_signals:
            cons_confidence = min(1.0, consensus_strength)
            verdict_components.append(
                VerdictComponent(
                    component_type="consensus",
                    provider="cross_agent_consensus",
                    model=None,
                    signals=consensus_signals,
                    confidence=cons_confidence,
                    reasoning_trace=f"Multiple agents reached consensus ({consensus_strength:.1%} alignment)",
                )
            )

        return threat_score, verdict_components

    def _extract_ai_signals(self, results: list[AgentResult]) -> list[EvidenceSignal]:
        """Extract structured signals from AI agent results."""
        signals: list[EvidenceSignal] = []

        for result in results:
            if isinstance(result, BehaviorResult):
                for ai_signal in result.ai_signals:
                    signals.append(
                        EvidenceSignal(
                            signal=ai_signal.name,
                            weight=0.85,  # High weight for direct AI reasoning
                            score_contribution=self._severity_to_points(ai_signal.severity),
                            confidence=ai_signal.confidence,
                            source=f"ai:{result.provider}",
                            detail=ai_signal.explanation,
                        )
                    )

            elif isinstance(result, OSINTResult):
                for ai_indicator in result.ai_indicators:
                    signals.append(
                        EvidenceSignal(
                            signal=ai_indicator.name,
                            weight=0.80,
                            score_contribution=self._severity_to_points(ai_indicator.severity),
                            confidence=ai_indicator.confidence,
                            source=f"ai:{result.provider}" if result.provider else "osint_ai",
                            detail=ai_indicator.evidence,
                        )
                    )

            elif isinstance(result, VisionResult):
                for artifact in result.ai_artifacts:
                    signals.append(
                        EvidenceSignal(
                            signal=artifact.artifact_type,
                            weight=0.75,
                            score_contribution=self._severity_to_points(artifact.severity),
                            confidence=artifact.confidence,
                            source=f"ai:{result.provider}",
                            detail=artifact.description,
                        )
                    )

            elif isinstance(result, AudioResult):
                for audio_sig in result.ai_signals:
                    signals.append(
                        EvidenceSignal(
                            signal=audio_sig.name,
                            weight=0.80,
                            score_contribution=self._severity_to_points(audio_sig.severity),
                            confidence=audio_sig.confidence,
                            source=f"ai:{result.provider}",
                            detail=audio_sig.explanation,
                        )
                    )

        return signals

    def _calculate_final_score(self, signals: list[EvidenceSignal]) -> int:
        """Calculate final threat score from all signals."""
        raw_score = sum(s.score_contribution for s in signals)
        return clamp_score(raw_score)

    def _calculate_aggregate_confidence(self, signals: list[EvidenceSignal]) -> float:
        """Calculate aggregate confidence from all signals."""
        if not signals:
            return 0.0
        confidence_sum = sum(s.confidence for s in signals)
        return confidence_sum / len(signals)

    def _determine_severity(self, score: int) -> ThreatSeverity:
        """Map score to severity level."""
        if score >= 80:
            return ThreatSeverity.CRITICAL
        elif score >= 60:
            return ThreatSeverity.HIGH
        elif score >= 40:
            return ThreatSeverity.MEDIUM
        return ThreatSeverity.LOW

    def _build_explanations(
        self,
        final_score: int,
        severity: ThreatSeverity,
        signals: list[EvidenceSignal],
        consensus_strength: float,
        web_summary: str = "",
        web_trust_delta: int = 0,
    ) -> tuple[str, str]:
        """Build human-readable and technical explanations."""
        top_signals = sorted(signals, key=lambda s: s.score_contribution, reverse=True)[:3]
        factors = [f.signal.replace("_", " ") for f in top_signals]

        simple_explanation = f"Threat level {severity.value.upper()}: "
        if factors:
            simple_explanation += f"Detected {', '.join(factors)}."
        else:
            simple_explanation += "No significant threats detected."

        if web_summary:
            simple_explanation += f" {web_summary}"

        if web_trust_delta < -15:
            simple_explanation += " Web verification confirmed legitimate company presence — score adjusted down."
        elif web_trust_delta > 10:
            simple_explanation += " Web verification found unverifiable or suspicious domain presence."

        # Technical explanation
        technical = f"Score: {final_score}/100 | Confidence: {self._calculate_aggregate_confidence(signals):.1%} | "
        technical += f"Signals: {len(signals)} | Consensus: {consensus_strength:.1%} | Web delta: {web_trust_delta:+d}"

        return simple_explanation[:2000], technical[:4000]

    @staticmethod
    def _extract_web_trust_delta(results: list[AgentResult]) -> int:
        """Extract trust delta from WebSearchAgent result."""
        for result in results:
            if isinstance(result, WebSearchResult):
                return result.trust_delta
        return 0

    @staticmethod
    def _extract_web_summary(results: list[AgentResult]) -> str:
        """Extract web summary from WebSearchAgent result."""
        for result in results:
            if isinstance(result, WebSearchResult):
                return result.web_summary
        return ""

    def _determine_verdict_source(
        self, ai_signals: list[EvidenceSignal], det_signals: list[EvidenceSignal], cons_signals: list[EvidenceSignal]
    ) -> str:
        """Determine primary source of verdict."""
        if cons_signals and len(cons_signals) >= 2:
            return "hybrid_correlation"
        elif ai_signals:
            return "ai_reasoning"
        elif det_signals:
            return "deterministic_validation"
        return "unknown"

    @staticmethod
    def _severity_to_points(severity: str) -> int:
        """Map severity to score points."""
        severity_map = {
            "critical": 25,
            "high": 18,
            "medium": 10,
            "low": 5,
        }
        return severity_map.get(severity.lower(), 8)

    @staticmethod
    def _extract_unique_factors(signals: list[EvidenceSignal]) -> list[str]:
        """Extract unique contributing factors."""
        return sorted(set(s.signal for s in signals))


class DeterministicValidator:
    """Deterministic validation layer for suspicious indicators."""

    async def validate(self, investigation_id: str, results: list[AgentResult]) -> list[EvidenceSignal]:
        """Run deterministic validation checks."""
        signals: list[EvidenceSignal] = []

        for result in results:
            if isinstance(result, BehaviorResult):
                # Validation checks on detected patterns
                if "payment_coercion" in result.detected_patterns:
                    signals.append(
                        EvidenceSignal(
                            signal="payment_coercion_confirmed",
                            weight=0.90,
                            score_contribution=22,
                            confidence=0.95,
                            source="deterministic_validation",
                            detail="Payment coercion pattern confirmed via deterministic validation",
                        )
                    )

            elif isinstance(result, OSINTResult):
                # Domain age validation
                if result.domain_age_days is not None and result.domain_age_days < 30:
                    signals.append(
                        EvidenceSignal(
                            signal="newly_registered_domain",
                            weight=0.82,
                            score_contribution=12,
                            confidence=0.98,
                            source="deterministic_validation",
                            detail=f"Domain registered {result.domain_age_days} days ago",
                        )
                    )

                # SSL validation
                if result.ssl_valid is False:
                    signals.append(
                        EvidenceSignal(
                            signal="invalid_tls",
                            weight=0.65,
                            score_contribution=8,
                            confidence=0.99,
                            source="deterministic_validation",
                            detail="SSL/TLS certificate invalid or missing",
                        )
                    )

        return signals


class ConsensusAnalyzer:
    """Analyzes consensus across multiple AI agents."""

    def analyze(self, results: list[AgentResult]) -> tuple[list[EvidenceSignal], float]:
        """Analyze cross-agent consensus.

        Returns:
            (consensus_signals, consensus_strength 0.0-1.0)
        """
        signals: list[EvidenceSignal] = []
        consensus_indicators: dict[str, int] = {}

        # Count indicator occurrences across agents
        for result in results:
            if isinstance(result, BehaviorResult):
                for pattern in result.detected_patterns:
                    consensus_indicators[pattern] = consensus_indicators.get(pattern, 0) + 1

            elif isinstance(result, OSINTResult):
                for indicator in result.suspicious_indicators:
                    consensus_indicators[indicator] = consensus_indicators.get(indicator, 0) + 1

            elif isinstance(result, AudioResult):
                for pattern in result.detected_patterns:
                    consensus_indicators[pattern] = consensus_indicators.get(pattern, 0) + 1

        # Create consensus signals for multi-agent agreement
        agent_count = len(results)
        for indicator, count in consensus_indicators.items():
            if count >= 2:  # Agreement between 2+ agents
                consensus_strength = min(1.0, count / agent_count)
                signals.append(
                    EvidenceSignal(
                        signal=f"{indicator}_consensus",
                        weight=0.88,
                        score_contribution=int(15 * consensus_strength),
                        confidence=min(1.0, 0.80 + (0.15 * consensus_strength)),
                        source="consensus_analysis",
                        detail=f"Detected by {count} independent agents",
                    )
                )

        # Calculate overall consensus strength
        consensus_strength = len([s for s in signals]) / max(1, len(consensus_indicators)) if consensus_indicators else 0.0

        return signals, consensus_strength
