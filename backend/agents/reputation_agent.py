"""
Reputation Intelligence Agent — evaluates educational value, exploitation signals,
and public trust quality for internship/recruitment opportunities.

This agent fills the gap between "outright scam" and "fully legitimate":
it identifies low-trust, low-value, or exploitative opportunities that are
technically legal but harmful to students and job seekers.

Uses NVIDIA NIM for reasoning.
"""

import time
import re
from providers.nvidia_client import reason, model_name as nvidia_model
from utils.json_recovery import recover_json

SYSTEM_PROMPT = """You are a Recruitment Trust Intelligence Analyst.

Your job is NOT to decide if something is a scam. Your job is to evaluate:
1. Educational and career VALUE of this internship/job opportunity
2. Exploitation signals — does this company extract value from interns without giving back?
3. Certificate farming — mass onboarding with no real mentorship or learning
4. Public trust quality — do students and professionals recommend this company?

TRUST DIMENSIONS to evaluate:

LEGITIMACY (is the company real and operating legitimately?)
- Company registration, valid domain, official contact channels
- Professional communication style

REPUTATION (what does the public say?)
- Glassdoor/AmbitionBox reviews about internship experience
- Reddit/Quora discussions about this company's internship quality
- Complaints about: no mentorship, certificate spam, mass hiring, low quality
- Positive signals: real projects, professional environment, strong alumni

EDUCATIONAL VALUE (is this worth a student's time?)
- Does the internship include real work, mentorship, skill development?
- Or is it "complete tasks, get certificate, no real learning"?
- Mass-onboarding internships (100s of interns at once) = LOW educational value
- Evidence of structured training, senior mentors, or real projects = HIGH value

FINANCIAL SAFETY (is there financial risk?)
- Any payment requirement = CRITICAL red flag
- UPI/crypto/bank transfer requests = SCAM territory
- No payment mentioned + no hints = safe on financial dimension

OPERATIONAL PROFESSIONALISM (how does the company operate?)
- Interview process quality (multi-round vs instant "you are selected")
- Communication via official email vs WhatsApp/Telegram only
- Clear role description vs vague "intern for us"
- Offer letter quality and professionalism

EXPLOITATION SIGNALS to detect:
- "pay2intern" patterns, task-completion certificates with no real learning
- Mass hiring (recruit 500+ interns simultaneously = suspect)  
- "Certificate of internship" as the primary benefit
- No stipend AND no real learning AND high time commitment
- Resume padding schemes — fake experience for CV
- "Complete these 5 tasks and you'll get a certificate" pipelines
- Social media marketing tasks disguised as internships

Return ONLY valid JSON:
{
  "trust_tier": "<LEGITIMATE | LOW_TRUST | SUSPICIOUS | HIGH_RISK | CRITICAL>",
  "legitimacy_score": <0-100>,
  "reputation_score": <0-100>,
  "educational_value_score": <0-100>,
  "financial_safety_score": <0-100>,
  "professionalism_score": <0-100>,
  "overall_trust_score": <0-100>,
  "exploitation_signals": ["specific exploitation pattern found"],
  "certificate_farming_detected": <true|false>,
  "mass_hiring_detected": <true|false>,
  "financial_risk": <true|false>,
  "educational_value_assessment": "<high|medium|low|unknown>",
  "trust_summary": "<2-3 sentence nuanced assessment>",
  "why_flagged": ["specific reason this was flagged at this trust tier"],
  "safe_signals": ["specific positive signal found"],
  "recommendation": "<clear, honest 1-2 sentence advice to the student/job seeker>"
}

Trust tier calibration:
- LEGITIMATE: Real company, positive reputation, meaningful learning, professional process, no red flags
- LOW_TRUST: Technically legal but weak educational value, mass onboarding, certificate-focused, poor mentorship reputation
- SUSPICIOUS: Mixed signals, unclear legitimacy, unusual patterns, inconsistent reputation
- HIGH_RISK: Strong scam indicators OR multiple exploitation patterns OR financial coercion
- CRITICAL: Active fraud, payment extraction, phishing, impersonation

IMPORTANT: Do NOT classify a company as HIGH_RISK or CRITICAL simply because:
- It's small or relatively unknown
- It offers unpaid internships (legal in many contexts)
- It has mixed reviews (use SUSPICIOUS or LOW_TRUST instead)
- It sends mass internship offers (use LOW_TRUST instead)

Reserve HIGH_RISK for strong fraud evidence. Reserve CRITICAL for clear active fraud."""


# Exploitation signal vocabulary for deterministic fallback
_EXPLOITATION_TERMS = [
    "certificate", "task-based", "complete tasks", "virtual internship",
    "mass hiring", "no stipend", "no mentorship", "no interview",
    "selected for internship", "congratulations you have been selected",
    "social media", "marketing intern", "resume farming", "pay2intern",
    "500 interns", "1000 interns", "batch of interns", "community of interns",
    "offer letter without interview", "fake experience",
]
_SAFE_TERMS = [
    "multi-round interview", "technical interview", "hr interview",
    "stipend", "paid internship", "mentorship", "senior engineer",
    "real projects", "official email", "nda", "onboarding plan",
    "structured training", "linkedin profile", "careers page",
]
_FINANCIAL_RISK_TERMS = [
    "deposit", "security fee", "registration fee", "upi", "gpay",
    "paytm", "phonepay", "payment", "pay before", "refundable fee",
    "equipment purchase", "training fee", "course fee",
]


def run(text: str, osint_result: dict | None = None, web_reputation: dict | None = None) -> dict:
    """Run reputation/trust intelligence analysis. Returns trust assessment dict."""
    start = time.time()

    # Inject OSINT and web context into the prompt if available
    context_parts = [f"Primary text/evidence:\n{text}"]
    if osint_result:
        context_parts.append(f"\nOSINT findings:\n"
                              f"Company: {osint_result.get('company_name', 'Unknown')}\n"
                              f"Legitimacy: {osint_result.get('company_legitimacy', '')}\n"
                              f"Flags: {osint_result.get('internship_flags', [])}")
    if web_reputation:
        context_parts.append(f"\nPublic web reputation conclusion: {web_reputation.get('conclusion', '')}\n"
                              f"Scam signals: {web_reputation.get('scam_signals', [])}\n"
                              f"Safe signals: {web_reputation.get('safe_signals', [])}\n"
                              f"Web summary: {web_reputation.get('summary', '')}")

    user_content = "\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Evaluate the trust quality of this recruitment opportunity:\n\n{user_content}"},
    ]

    try:
        raw = reason(messages, max_tokens=1000)
        parsed = recover_json(raw)
        if not parsed:
            return _heuristic_reputation(text, osint_result, web_reputation, start)
        parsed["provider"] = nvidia_model()
        parsed["latency_ms"] = int((time.time() - start) * 1000)
        return parsed
    except RuntimeError as e:
        fallback = _heuristic_reputation(text, osint_result, web_reputation, start)
        fallback["provider"] = f"local_heuristic_after_{nvidia_model()}_failure"
        fallback["error"] = str(e)
        return fallback


def _heuristic_reputation(
    text: str,
    osint_result: dict | None,
    web_reputation: dict | None,
    start: float,
) -> dict:
    """Deterministic fallback reputation analysis."""
    lowered = text.lower()

    exploitation_hits = [t for t in _EXPLOITATION_TERMS if t in lowered]
    safe_hits = [t for t in _SAFE_TERMS if t in lowered]
    financial_risk = any(t in lowered for t in _FINANCIAL_RISK_TERMS)

    # Absorb OSINT signals
    if osint_result:
        flags = [str(f).lower() for f in osint_result.get("internship_flags", [])]
        exploitation_hits += [f for f in flags if f and f not in exploitation_hits]

    # Absorb web reputation
    web_scam_signals = []
    if web_reputation:
        web_scam_signals = [str(s).lower() for s in (web_reputation.get("scam_signals") or [])]

    certificate_farming = any(
        t in lowered for t in ["certificate", "task", "complete tasks", "virtual internship"]
    ) and not any(t in lowered for t in ["real project", "mentorship", "stipend", "interview"])

    mass_hiring = any(
        re.search(p, lowered) for p in [
            r"\d{3,}\s+intern", r"batch of intern", r"community of intern",
            r"500\+|1000\+|selected from", r"mass hiring",
        ]
    )

    # Score dimensions
    financial_safety = 20 if financial_risk else 85
    educational_value = max(10, 60 - len(exploitation_hits) * 8 + len(safe_hits) * 6)
    professionalism = max(10, 70 - len(exploitation_hits) * 5 + len(safe_hits) * 8)
    legitimacy = 70 if not financial_risk else 30
    reputation = max(20, 65 - len(web_scam_signals) * 10)

    overall = int((financial_safety * 0.3 + educational_value * 0.25 + professionalism * 0.2 + legitimacy * 0.15 + reputation * 0.1))

    # Determine trust tier
    if financial_risk or len(web_scam_signals) >= 3:
        trust_tier = "HIGH_RISK"
    elif certificate_farming or mass_hiring or len(exploitation_hits) >= 3:
        trust_tier = "LOW_TRUST"
    elif len(exploitation_hits) >= 1 or len(web_scam_signals) >= 1:
        trust_tier = "SUSPICIOUS"
    elif safe_hits and not exploitation_hits:
        trust_tier = "LEGITIMATE"
    else:
        trust_tier = "SUSPICIOUS"

    why_flagged = exploitation_hits[:4] + web_scam_signals[:2]

    rec = (
        "Do not pay any fees. Stop engagement immediately and verify through official channels."
        if financial_risk
        else "Proceed with caution. Verify the role's educational value and mentorship structure before committing your time."
        if trust_tier in ("LOW_TRUST", "SUSPICIOUS")
        else "This opportunity appears trustworthy. Confirm details through official channels."
    )

    return {
        "trust_tier": trust_tier,
        "legitimacy_score": legitimacy,
        "reputation_score": reputation,
        "educational_value_score": educational_value,
        "financial_safety_score": financial_safety,
        "professionalism_score": professionalism,
        "overall_trust_score": overall,
        "exploitation_signals": exploitation_hits[:5],
        "certificate_farming_detected": certificate_farming,
        "mass_hiring_detected": mass_hiring,
        "financial_risk": financial_risk,
        "educational_value_assessment": "low" if certificate_farming else "medium" if exploitation_hits else "unknown",
        "trust_summary": f"Deterministic fallback: found {len(exploitation_hits)} exploitation signal(s) and {len(web_scam_signals)} web scam signal(s).",
        "why_flagged": why_flagged or ["insufficient evidence to determine trust level"],
        "safe_signals": safe_hits[:4],
        "recommendation": rec,
        "provider": "local_heuristic",
        "latency_ms": int((time.time() - start) * 1000),
    }
