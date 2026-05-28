"""
Consensus Agent — merges all agent signals into a final verdict.
Uses NVIDIA NIM for final reasoning synthesis.
"""

import time
import json
from providers.nvidia_client import reason, model_name as nvidia_model
from utils.json_recovery import recover_json

SYSTEM_PROMPT = """You are a senior recruitment fraud analyst synthesizing evidence from multiple intelligence agents.

You will receive:
- Behavior analysis (LLM-based)
- OSINT findings (LLM-based)
- Domain intelligence (deterministic)
- Optional: image analysis (vision AI)

Produce a final verdict. Return ONLY a JSON object:
{
  "verdict": "<one of: SAFE | LOW RISK | MEDIUM RISK | HIGH RISK | CRITICAL>",
  "confidence": <integer 0-100>,
  "headline": "<one sentence headline for this case>",
  "why_flagged": ["specific reason 1", "specific reason 2"],
  "safe_signals": ["reassuring signal 1"],
  "recommendation": "<clear 1-2 sentence actionable advice>",
  "reasoning": "<2-3 sentence explanation of the synthesis>"
}

CRITICAL RULE: Be calibrated. Do NOT aggressively assume scams.
- Standard corporate hiring processes with official email domains = SAFE
- Payment requests + suspicious domains + Telegram-only = CRITICAL
- Weigh ALL evidence — both flags AND safe signals.

Scoring guide:
- SAFE: No red flags, official channels, standard process
- LOW RISK: Minor concerns but mostly legitimate indicators
- MEDIUM RISK: Mixed signals, exercise caution
- HIGH RISK: Multiple fraud indicators present
- CRITICAL: Clear and present scam — do not engage"""


def run(
    behavior: dict,
    osint: dict,
    domain: dict,
    image_analysis: str | None = None,
) -> dict:
    """
    Synthesize all agent outputs into a final verdict.
    Returns consensus dict.
    """
    start = time.time()

    evidence = {
        "behavior_analysis": {
            "signals": behavior.get("signals", []),
            "safe_indicators": behavior.get("safe_indicators", []),
            "risk_score": behavior.get("risk_score", 0),
            "reasoning": behavior.get("reasoning", ""),
        },
        "osint_findings": {
            "company_legitimacy": osint.get("company_legitimacy", ""),
            "onboarding_assessment": osint.get("onboarding_assessment", ""),
            "key_findings": osint.get("key_findings", []),
            "risk_score": osint.get("risk_score", 0),
        },
        "domain_intelligence": {
            "domains_found": domain.get("domains_found", []),
            "risk_score": domain.get("risk_score", 5),
            "summary": domain.get("summary", ""),
        },
    }

    if image_analysis:
        evidence["image_analysis"] = image_analysis

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Synthesize this evidence into a final verdict:\n\n{json.dumps(evidence, indent=2)}",
        },
    ]

    try:
        raw = reason(messages, max_tokens=900)
        parsed = recover_json(raw)
        if not parsed:
            # Fallback: compute from raw scores
            avg_score = (
                behavior.get("risk_score", 0)
                + osint.get("risk_score", 0)
                + domain.get("risk_score", 5)
            ) // 3
            verdict = _score_to_verdict(avg_score)
            return {
                "verdict": verdict,
                "confidence": 50,
                "headline": f"Analysis complete — {verdict}",
                "why_flagged": behavior.get("signals", [])[:3],
                "safe_signals": behavior.get("safe_indicators", [])[:2],
                "recommendation": "Review the technical analysis for details.",
                "reasoning": "Consensus synthesis could not be parsed; verdict estimated from agent scores.",
                "provider": nvidia_model(),
                "latency_ms": int((time.time() - start) * 1000),
                "error": "json_parse_failed",
            }
        parsed["provider"] = nvidia_model()
        parsed["latency_ms"] = int((time.time() - start) * 1000)
        return parsed
    except RuntimeError as e:
        avg_score = (
            behavior.get("risk_score", 0)
            + osint.get("risk_score", 0)
            + domain.get("risk_score", 5)
        ) // 3
        verdict = _score_to_verdict(avg_score)
        return {
            "verdict": verdict,
            "confidence": 40,
            "headline": f"Analysis complete — {verdict} (degraded mode)",
            "why_flagged": behavior.get("signals", [])[:3],
            "safe_signals": behavior.get("safe_indicators", [])[:2],
            "recommendation": "Consensus agent encountered an error. Review individual agent findings.",
            "reasoning": f"Consensus agent failed: {e}",
            "provider": nvidia_model(),
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }


def _score_to_verdict(score: int) -> str:
    if score < 20:
        return "SAFE"
    if score < 40:
        return "LOW RISK"
    if score < 55:
        return "MEDIUM RISK"
    if score < 75:
        return "HIGH RISK"
    return "CRITICAL"
