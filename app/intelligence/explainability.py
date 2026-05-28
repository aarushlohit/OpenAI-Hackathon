"""Explainability and live thinking stream engine.

Implements:
1. Human-readable explanations for verdicts
2. Technical trace explanations for developers
3. Live thinking stream of investigation progress
4. Evidence breakdown with reasoning
"""

import json
import logging
from datetime import datetime

from app.models.threat_score import EvidenceSignal, ThreatScore, ThreatSeverity

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """Generates human-readable and technical explanations for verdicts."""

    @staticmethod
    def generate_human_explanation(threat_score: ThreatScore, verdict_source: str) -> str:
        """Generate plain-language explanation of the verdict.

        Format:
        [VERDICT]: Risk is HIGH/LOW/etc.
        [REASON]: Detected X, Y, Z patterns.
        [ACTION]: Consider Y.
        """
        verdict_emoji = ExplainabilityEngine._get_verdict_emoji(threat_score.severity)
        verdict_text = f"{verdict_emoji} **{threat_score.severity.upper()} THREAT**"

        factors = threat_score.contributing_factors[:5]
        factors_text = " • ".join(factors) if factors else "No specific factors identified"

        action_map = {
            ThreatSeverity.CRITICAL: "Immediately isolate and escalate. Do not proceed.",
            ThreatSeverity.HIGH: "Review carefully before engagement. Verify independently.",
            ThreatSeverity.MEDIUM: "Investigate further. Apply caution.",
            ThreatSeverity.LOW: "Monitor but likely safe. Standard verification recommended.",
        }

        explanation = f"""{verdict_text}

Evidence:
{factors_text}

Summary: {threat_score.explanation}

Recommendation: {action_map.get(threat_score.severity, 'Review carefully.')}

Produced By: {ExplainabilityEngine._get_producer_attribution(verdict_source)}
"""
        return explanation.strip()

    @staticmethod
    def generate_technical_explanation(threat_score: ThreatScore, verdict_source: str) -> str:
        """Generate detailed technical explanation for SOC/developer review."""
        signals_breakdown = ExplainabilityEngine._build_signals_breakdown(threat_score.evidence_breakdown)

        explanation = f"""=== TECHNICAL THREAT ANALYSIS ===

VERDICT METADATA:
  Score: {threat_score.final_score}/100
  Confidence: {threat_score.confidence:.1%}
  Severity: {threat_score.severity.upper()}
  Verdict Source: {verdict_source}
  Primary Cognition: {threat_score.primary_cognition}
  Deterministic Validation: {"✓" if threat_score.deterministic_validation else "✗"}
  Cross-Agent Consensus: {"✓" if threat_score.cross_agent_consensus else "✗"}

SIGNAL BREAKDOWN:
{signals_breakdown}

CONTRIBUTING FACTORS:
{", ".join(threat_score.contributing_factors) or "None identified"}

FULL ANALYSIS:
{threat_score.explainability_summary}
"""
        return explanation.strip()

    @staticmethod
    def _build_signals_breakdown(signals: list[EvidenceSignal]) -> str:
        """Build detailed breakdown of contributing signals."""
        if not signals:
            return "  (No signals)"

        lines = []
        for sig in sorted(signals, key=lambda s: s.score_contribution, reverse=True)[:10]:
            contribution = f"({sig.score_contribution} pts)"
            confidence = f"[{sig.confidence:.0%}]"
            source = f"{sig.source}"
            lines.append(f"  • {sig.signal} {contribution} {confidence} — {sig.detail[:100] or source}")

        return "\n".join(lines)

    @staticmethod
    def _get_verdict_emoji(severity: ThreatSeverity) -> str:
        """Get emoji for verdict severity."""
        emoji_map = {
            ThreatSeverity.CRITICAL: "🚨",
            ThreatSeverity.HIGH: "⚠️",
            ThreatSeverity.MEDIUM: "⚡",
            ThreatSeverity.LOW: "✓",
        }
        return emoji_map.get(severity, "❓")

    @staticmethod
    def _get_producer_attribution(verdict_source: str) -> str:
        """Get human-readable producer attribution."""
        producer_map = {
            "ai_reasoning": "🧠 AI Model (NVIDIA Nemotron Omni)",
            "deterministic_validation": "🛡️ Deterministic Engine",
            "hybrid_correlation": "🔀 Hybrid Correlation (AI + Deterministic + Consensus)",
        }
        return producer_map.get(verdict_source, "Unknown Provider")


class LiveThinkingStream:
    """Generates event stream of live investigation thinking.

    Emits progress events like:
    - "Analyzing recruiter language..."
    - "Evaluating onboarding legitimacy..."
    - "Cross-validating multimodal evidence..."
    - "Building threat graph..."
    """

    @staticmethod
    def get_stream_events(investigation_phase: str) -> list[dict]:
        """Get live thinking events for current investigation phase.

        Phases:
        - intake: initial processing
        - behavior_analysis: AI analyzing communication
        - osint: domain and reputation analysis
        - vision: document and image analysis
        - audio: voice analysis
        - correlation: cross-agent analysis
        - verdict: final synthesis
        """
        phase_events: dict[str, list[dict]] = {
            "intake": [
                {
                    "thinking": "Validating input format...",
                    "status": "processing",
                    "timestamp_offset": 0.1,
                },
                {
                    "thinking": "Extracting investigation targets...",
                    "status": "processing",
                    "timestamp_offset": 0.3,
                },
            ],
            "behavior_analysis": [
                {
                    "thinking": "Analyzing recruiter language patterns...",
                    "status": "processing",
                    "timestamp_offset": 0.0,
                },
                {
                    "thinking": "Detecting urgency and coercion signals...",
                    "status": "processing",
                    "timestamp_offset": 0.4,
                },
                {
                    "thinking": "Evaluating payment extraction tactics...",
                    "status": "processing",
                    "timestamp_offset": 0.8,
                },
                {
                    "thinking": "Assessing impersonation risk...",
                    "status": "processing",
                    "timestamp_offset": 1.2,
                },
            ],
            "osint": [
                {
                    "thinking": "Evaluating domain age and registration...",
                    "status": "processing",
                    "timestamp_offset": 0.0,
                },
                {
                    "thinking": "Checking domain reputation indicators...",
                    "status": "processing",
                    "timestamp_offset": 0.5,
                },
                {
                    "thinking": "Analyzing WHOIS anomalies...",
                    "status": "processing",
                    "timestamp_offset": 1.0,
                },
            ],
            "vision": [
                {
                    "thinking": "Extracting text from visual evidence...",
                    "status": "processing",
                    "timestamp_offset": 0.0,
                },
                {
                    "thinking": "Detecting document forgery indicators...",
                    "status": "processing",
                    "timestamp_offset": 0.6,
                },
                {
                    "thinking": "Analyzing company branding authenticity...",
                    "status": "processing",
                    "timestamp_offset": 1.0,
                },
            ],
            "audio": [
                {
                    "thinking": "Transcribing audio evidence...",
                    "status": "processing",
                    "timestamp_offset": 0.0,
                },
                {
                    "thinking": "Detecting coercive tone and pressure tactics...",
                    "status": "processing",
                    "timestamp_offset": 1.0,
                },
                {
                    "thinking": "Recognizing urgency and manipulation language...",
                    "status": "processing",
                    "timestamp_offset": 1.5,
                },
            ],
            "correlation": [
                {
                    "thinking": "Cross-validating signals from all agents...",
                    "status": "processing",
                    "timestamp_offset": 0.0,
                },
                {
                    "thinking": "Computing consensus strength...",
                    "status": "processing",
                    "timestamp_offset": 0.5,
                },
                {
                    "thinking": "Running deterministic validation layer...",
                    "status": "processing",
                    "timestamp_offset": 1.0,
                },
                {
                    "thinking": "Building threat graph correlations...",
                    "status": "processing",
                    "timestamp_offset": 1.5,
                },
            ],
            "verdict": [
                {
                    "thinking": "Reconciling AI reasoning with deterministic checks...",
                    "status": "processing",
                    "timestamp_offset": 0.0,
                },
                {
                    "thinking": "Computing final threat score...",
                    "status": "processing",
                    "timestamp_offset": 0.5,
                },
                {
                    "thinking": "Generating explainability narrative...",
                    "status": "processing",
                    "timestamp_offset": 1.0,
                },
                {
                    "thinking": "Finalizing verdict and attribution...",
                    "status": "complete",
                    "timestamp_offset": 1.5,
                },
            ],
        }

        return phase_events.get(investigation_phase, [])

    @staticmethod
    def format_event_stream(events: list[dict]) -> list[str]:
        """Format events for websocket streaming or display."""
        formatted = []
        for event in events:
            formatted.append(f"⏳ {event['thinking']}")
        return formatted


class DebugModeExplainability:
    """Extended explanations for debug/developer mode."""

    @staticmethod
    def generate_full_trace(threat_score: ThreatScore, verdict_source: str, agent_results: list = None) -> str:
        """Generate complete trace including all events and decisions."""
        trace = f"""=== COMPLETE INVESTIGATION TRACE ===

INVESTIGATION_ID: {threat_score.investigation_id}
EVALUATION_TIMESTAMP: {datetime.utcnow().isoformat()}Z

VERDICT SUMMARY:
  Score: {threat_score.final_score}/100
  Severity: {threat_score.severity.upper()}
  Confidence: {threat_score.confidence:.1%}
  Source: {verdict_source}
  Primary Cognition: {threat_score.primary_cognition}

DETERMINISTIC VALIDATION: {"PASSED ✓" if threat_score.deterministic_validation else "FAILED ✗"}
CROSS_AGENT_CONSENSUS: {"REACHED ✓" if threat_score.cross_agent_consensus else "NOT REACHED ✗"}

SIGNALS TRACE:
{DebugModeExplainability._trace_signals(threat_score.evidence_breakdown)}

CONTRIBUTING FACTORS:
{chr(10).join(f"  • {f}" for f in threat_score.contributing_factors[:20])}

EXPLANATION:
{threat_score.explainability_summary}

HUMAN_SUMMARY:
{ExplainabilityEngine.generate_human_explanation(threat_score, verdict_source)}
"""
        return trace

    @staticmethod
    def _trace_signals(signals: list[EvidenceSignal]) -> str:
        """Build detailed signal trace."""
        lines = []
        by_source = {}
        for sig in signals:
            by_source.setdefault(sig.source, []).append(sig)

        for source, source_signals in sorted(by_source.items()):
            lines.append(f"\n  SOURCE: {source}")
            for sig in sorted(source_signals, key=lambda s: s.score_contribution, reverse=True):
                lines.append(
                    f"    {sig.signal:30s} | {sig.score_contribution:3d}pts | "
                    f"{sig.confidence:0%} | {sig.detail[:60]}"
                )

        return "\n".join(lines)
