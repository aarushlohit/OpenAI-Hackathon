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
- OSINT findings (LLM-based — includes company legitimacy assessment and internship-specific flags)
- Domain intelligence (deterministic)
- Optional: structured image extraction (Pollinations vision/OCR)
- Optional: Web reputation search across Glassdoor, AmbitionBox, Reddit, Quora, and scam reports
  (includes REAL web snippets from actual searches — treat these as ground truth)

CRITICAL RULES FOR ACCURACY:
1. "Company is registered" is NOT a safe signal. Scammers routinely misuse real registered companies.
2. If web_reputation.registered_but_suspicious = true, treat this as a HIGH RISK escalation.
3. If ANY web source (Reddit, Quora, scam-report) shows a complaint about THIS company's internship
   asking for UPI, deposit, or certificate-based schemes, escalate to HIGH RISK or CRITICAL.
4. If behavior_analysis shows payment/deposit/Telegram signals AND web searches show no legitimate
   hiring evidence, escalate to CRITICAL.
5. Never give SAFE or LOW RISK if:
   - Deposits or UPI payments are mentioned
   - Telegram-only onboarding is the only contact method
   - OSINT flags company_legitimacy as REAL_BUT_SUSPICIOUS or IMPERSONATION
   - Web reputation conclusion is SCAM or registered_but_suspicious is true

Produce a final verdict. Return ONLY a JSON object:
{
  "verdict": "<one of: SAFE | LOW RISK | MEDIUM RISK | HIGH RISK | CRITICAL>",
  "confidence": <integer 0-100>,
  "headline": "<one sentence headline for this case>",
  "why_flagged": ["specific reason 1 — cite which agent found it", "specific reason 2"],
  "safe_signals": ["reassuring signal 1"],
  "recommendation": "<clear 1-2 sentence actionable advice>",
  "reasoning": "<3-4 sentence explanation of the synthesis — reference actual evidence>"
}

Scoring guide:
- SAFE: No red flags, official channels, standard multi-round process, confirmed employer reputation
- LOW RISK: Minor concerns but mostly legitimate indicators, verify via official company page
- MEDIUM RISK: Mixed signals, one or two suspicious patterns, exercise caution
- HIGH RISK: Multiple fraud indicators OR web complaints about this company's internships
- CRITICAL: Clear and present scam — payment/deposit/Telegram + no legitimate hiring evidence"""


def run(
    behavior: dict,
    osint: dict,
    domain: dict,
    image_analysis: dict | str | None = None,
    web_reputation: dict | None = None,
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
            "company_name": osint.get("company_name", "Unknown"),
            "company_legitimacy": osint.get("company_legitimacy", ""),
            "onboarding_assessment": osint.get("onboarding_assessment", ""),
            "recruiter_credibility": osint.get("recruiter_credibility", ""),
            "internship_flags": osint.get("internship_flags", []),
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
    if web_reputation:
        evidence["web_reputation"] = web_reputation

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
        score = _fallback_score(behavior, osint, domain, image_analysis, web_reputation)
        verdict = _score_to_verdict(score)
        why_flagged = _collect_fallback_flags(behavior, domain, image_analysis, web_reputation)
        return {
            "verdict": verdict,
            "confidence": 68 if score >= 55 else 45,
            "headline": f"Analysis complete — {verdict} (degraded mode)",
            "why_flagged": why_flagged[:6],
            "safe_signals": behavior.get("safe_indicators", [])[:2],
            "recommendation": "Treat this as unresolved risk until the flagged evidence is verified through official company channels. Do not pay fees or continue Telegram-only onboarding.",
            "reasoning": f"Primary consensus model failed: {e}. Degraded verdict was computed from behavior, domain, image, and web reputation scores instead of defaulting to SAFE.",
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


def _fallback_score(
    behavior: dict,
    osint: dict,
    domain: dict,
    image_analysis: dict | str | None,
    web_reputation: dict | None,
) -> int:
    scores = [
        int(behavior.get("risk_score", 0) or 0),
        int(osint.get("risk_score", 0) or 0),
        int(domain.get("risk_score", 5) or 5),
    ]
    if isinstance(image_analysis, dict):
        scores.append(int(image_analysis.get("risk_score", 0) or 0))
        if str(image_analysis.get("scam_conclusion", "")).upper() == "SCAM":
            scores.append(90)
    if web_reputation:
        if str(web_reputation.get("conclusion", "")).upper() == "SCAM":
            scores.append(90)
        confidence = web_reputation.get("confidence")
        if isinstance(confidence, (int, float)):
            scores.append(int(confidence * 100 if 0 <= confidence <= 1 else confidence))
    return max(scores)


def _collect_fallback_flags(
    behavior: dict,
    domain: dict,
    image_analysis: dict | str | None,
    web_reputation: dict | None,
) -> list[str]:
    flags = [str(item) for item in behavior.get("signals", [])]
    flags.extend(str(item) for item in domain.get("all_signals", []))
    if isinstance(image_analysis, dict):
        flags.extend(str(item) for item in image_analysis.get("red_flags", []))
        if image_analysis.get("error"):
            flags.append(f"Image extraction degraded: {image_analysis['error']}")
    if web_reputation:
        flags.extend(str(item) for item in web_reputation.get("scam_signals", []))
        if web_reputation.get("error"):
            flags.append(f"Web reputation degraded: {web_reputation['error']}")
    return list(dict.fromkeys(flags))
