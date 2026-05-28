"""
Consensus Agent — merges all agent signals into a final trust verdict.
Uses NVIDIA NIM for final reasoning synthesis.

UPGRADED: Now produces multi-dimensional trust intelligence verdicts
instead of binary scam/not-scam classification.
"""

import time
import json
from providers.nvidia_client import reason, model_name as nvidia_model
from utils.json_recovery import recover_json

SYSTEM_PROMPT = """You are a Senior Recruitment Trust Intelligence Analyst.

You synthesize evidence from multiple AI agents to produce a nuanced, multi-dimensional
trust verdict — NOT a binary scam/not-scam classification.

You will receive:
- Behavior analysis (LLM-based): fraud signal detection
- OSINT findings (LLM-based): company legitimacy + onboarding assessment
- Domain intelligence (deterministic): domain trust signals
- Reputation intelligence (LLM-based): educational value, exploitation signals, public trust
- Optional: image extraction (Pollinations vision/OCR)
- Optional: web reputation search (Glassdoor, AmbitionBox, Reddit, Quora)

== THE 5 TRUST TIERS ==

1. LEGITIMATE
   Trusted company, professional hiring, strong public reputation, safe onboarding.
   Example: Google, Microsoft, Amazon, well-regarded local companies.

2. LOW TRUST OPPORTUNITY
   Technically legal, but: weak educational value, mass onboarding, certificate-farming,
   poor mentorship reputation, no meaningful learning. NOT a scam, but NOT recommended
   for career growth unless the student only wants a certificate.
   Example: Mass virtual internship providers, certificate-focused platforms.

3. SUSPICIOUS
   Mixed signals. Inconsistent reputation, unusual onboarding, unclear legitimacy.
   Cannot be classified as safe OR as scam/high-risk with current evidence.

4. HIGH RISK
   Strong scam indicators: payment coercion, phishing domain, fake recruiter,
   impersonation, OR multiple severe exploitation patterns.

5. CRITICAL
   Active fraud: payment extraction, phishing infrastructure, typo-squatting,
   financial extraction attempt, malicious onboarding.

== TRUST DIMENSIONS TO WEIGH ==

LEGITIMACY: Company registration, valid domain, official contact channels
REPUTATION: Public reviews, Reddit/Glassdoor/AmbitionBox sentiment, scam discussions
EDUCATIONAL VALUE: Real learning, mentorship, structured work vs certificate farming
FINANCIAL SAFETY: Payment requests, UPI, fees, equipment purchase
OPERATIONAL PROFESSIONALISM: Interview quality, communication, offer letter standards

== CRITICAL CALIBRATION RULES ==

DO NOT classify as HIGH RISK or CRITICAL unless:
- Money extraction / payment coercion is present
- Phishing domain or impersonation is found
- Active fraud indicators are confirmed

DO classify as LOW TRUST OPPORTUNITY when:
- Company is registered and not phishing
- But reputation shows mass hiring, certificate farming, poor mentorship
- Or educational value is very low despite no fraud

DO classify as SUSPICIOUS when:
- Mixed signals exist
- Cannot confirm legitimacy OR fraud
- Reputation is unclear

SAFE SIGNALS that should reduce risk significantly:
- Official company domain (not free/suspicious TLD)
- No payment request mentioned anywhere
- Verified company registration
- Standard multi-round interview process
- Professional offer letter structure
- Positive public reviews on reputable platforms

Return ONLY valid JSON:
{
  "verdict": "<LEGITIMATE | LOW TRUST OPPORTUNITY | SUSPICIOUS | HIGH RISK | CRITICAL>",
  "confidence": <integer 0-100>,
  "headline": "<one sentence headline summarizing the trust assessment>",
  "trust_dimensions": {
    "legitimacy": <0-100>,
    "reputation": <0-100>,
    "educational_value": <0-100>,
    "financial_safety": <0-100>,
    "professionalism": <0-100>
  },
  "why_flagged": ["specific reason 1 — cite which agent found it", "reason 2"],
  "safe_signals": ["reassuring signal 1", "signal 2"],
  "exploitation_signals": ["exploitation pattern found, if any"],
  "recommendation": "<clear 1-2 sentence actionable advice>",
  "reasoning": "<3-4 sentence explanation citing actual evidence>"
}"""


def run(
    behavior: dict,
    osint: dict,
    domain: dict,
    reputation: dict | None = None,
    image_analysis: dict | str | None = None,
    web_reputation: dict | None = None,
) -> dict:
    """Synthesize all agent outputs into a final trust verdict."""
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

    if reputation:
        evidence["reputation_intelligence"] = {
            "trust_tier": reputation.get("trust_tier", ""),
            "educational_value_score": reputation.get("educational_value_score", 50),
            "overall_trust_score": reputation.get("overall_trust_score", 50),
            "exploitation_signals": reputation.get("exploitation_signals", []),
            "certificate_farming_detected": reputation.get("certificate_farming_detected", False),
            "mass_hiring_detected": reputation.get("mass_hiring_detected", False),
            "financial_risk": reputation.get("financial_risk", False),
            "educational_value_assessment": reputation.get("educational_value_assessment", "unknown"),
            "trust_summary": reputation.get("trust_summary", ""),
        }

    if image_analysis:
        evidence["image_analysis"] = image_analysis
    if web_reputation:
        evidence["web_reputation"] = {
            "conclusion": web_reputation.get("conclusion", ""),
            "registered_but_suspicious": web_reputation.get("registered_but_suspicious", False),
            "scam_signals": web_reputation.get("scam_signals", []),
            "safe_signals": web_reputation.get("safe_signals", []),
            "summary": web_reputation.get("summary", ""),
        }

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Synthesize this multi-dimensional evidence into a trust verdict:\n\n{json.dumps(evidence, indent=2)}",
        },
    ]

    try:
        raw = reason(messages, max_tokens=1000)
        parsed = recover_json(raw)
        if not parsed:
            return _fallback_verdict(behavior, osint, domain, reputation, image_analysis, web_reputation, start)
        parsed["provider"] = nvidia_model()
        parsed["latency_ms"] = int((time.time() - start) * 1000)
        return parsed
    except RuntimeError as e:
        result = _fallback_verdict(behavior, osint, domain, reputation, image_analysis, web_reputation, start)
        result["error"] = str(e)
        return result


def _verdict_from_scores(
    behavior_score: int,
    osint_score: int,
    domain_score: int,
    reputation_trust_score: int,
    financial_risk: bool,
    exploitation_count: int,
    web_conclusion: str,
) -> str:
    """Map multi-dimensional signals to a trust verdict."""
    # CRITICAL: Active fraud
    if financial_risk and (behavior_score >= 70 or web_conclusion == "SCAM"):
        return "CRITICAL"

    # HIGH RISK: Strong fraud indicators
    if financial_risk or web_conclusion == "SCAM" or behavior_score >= 75 or domain_score >= 75:
        return "HIGH RISK"

    # Compute composite trust score
    composite = (behavior_score * 0.3 + osint_score * 0.25 + domain_score * 0.15 +
                 (100 - reputation_trust_score) * 0.3)

    if composite >= 70:
        return "HIGH RISK"
    if composite >= 50 or exploitation_count >= 2:
        return "SUSPICIOUS"
    if exploitation_count >= 1 or reputation_trust_score < 45:
        return "LOW TRUST OPPORTUNITY"
    if composite < 20 and reputation_trust_score >= 65:
        return "LEGITIMATE"
    return "SUSPICIOUS"


def _fallback_verdict(
    behavior: dict,
    osint: dict,
    domain: dict,
    reputation: dict | None,
    image_analysis: dict | str | None,
    web_reputation: dict | None,
    start: float,
) -> dict:
    """Deterministic fallback when the LLM fails."""
    behavior_score = int(behavior.get("risk_score", 0) or 0)
    osint_score = int(osint.get("risk_score", 0) or 0)
    domain_score = int(domain.get("risk_score", 5) or 5)
    reputation_trust_score = int((reputation or {}).get("overall_trust_score", 50) or 50)
    financial_risk = bool((reputation or {}).get("financial_risk", False))
    exploitation_count = len((reputation or {}).get("exploitation_signals", []))
    web_conclusion = str((web_reputation or {}).get("conclusion", "")).upper()

    # Image escalation
    if isinstance(image_analysis, dict):
        if str(image_analysis.get("scam_conclusion", "")).upper() == "SCAM":
            behavior_score = max(behavior_score, 80)
        img_score = image_analysis.get("risk_score")
        if isinstance(img_score, (int, float)):
            behavior_score = max(behavior_score, int(img_score))

    verdict = _verdict_from_scores(
        behavior_score, osint_score, domain_score, reputation_trust_score,
        financial_risk, exploitation_count, web_conclusion
    )

    # Collect flags
    flags = [str(s) for s in behavior.get("signals", [])]
    flags += [str(s) for s in domain.get("all_signals", [])]
    if reputation:
        flags += [str(s) for s in reputation.get("exploitation_signals", [])]
        flags += [str(s) for s in reputation.get("why_flagged", [])]
    if web_reputation:
        flags += [str(s) for s in web_reputation.get("scam_signals", [])]
    if isinstance(image_analysis, dict):
        flags += [str(s) for s in image_analysis.get("red_flags", [])]

    safe = [str(s) for s in behavior.get("safe_indicators", [])]
    if reputation:
        safe += [str(s) for s in reputation.get("safe_signals", [])]
    if web_reputation:
        safe += [str(s) for s in web_reputation.get("safe_signals", [])]

    exploitation = list(dict.fromkeys([str(s) for s in (reputation or {}).get("exploitation_signals", [])]))

    rec = (
        "Do not proceed. Stop all engagement and do not share personal or financial information."
        if verdict == "CRITICAL"
        else "Exercise strong caution. Independently verify through official company channels before sharing documents or data."
        if verdict == "HIGH RISK"
        else "Verify this opportunity carefully. Check if real learning, mentorship, and structured work are offered before committing your time."
        if verdict in ("SUSPICIOUS", "LOW TRUST OPPORTUNITY")
        else "This opportunity appears trustworthy. Confirm details through official company channels before proceeding."
    )

    return {
        "verdict": verdict,
        "confidence": 55,
        "headline": f"Trust assessment complete — {verdict} (degraded mode)",
        "trust_dimensions": {
            "legitimacy": max(0, 100 - osint_score),
            "reputation": max(0, 100 - (len(flags) * 10)),
            "educational_value": reputation_trust_score if reputation else 50,
            "financial_safety": 20 if financial_risk else 85,
            "professionalism": max(0, 100 - behavior_score),
        },
        "why_flagged": list(dict.fromkeys(flags))[:6],
        "safe_signals": list(dict.fromkeys(safe))[:4],
        "exploitation_signals": exploitation[:4],
        "recommendation": rec,
        "reasoning": (
            f"Degraded mode: consensus LLM failed. Verdict estimated from behavior score {behavior_score}, "
            f"OSINT score {osint_score}, domain score {domain_score}, and reputation trust score {reputation_trust_score}."
        ),
        "provider": nvidia_model(),
        "latency_ms": int((time.time() - start) * 1000),
        "error": "json_parse_failed",
    }
