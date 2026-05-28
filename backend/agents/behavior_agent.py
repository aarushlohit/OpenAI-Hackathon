"""
Behavior Agent — detects fraud signals in text using NVIDIA NIM.
"""

import time
from providers.nvidia_client import reason, model_name as nvidia_model
from utils.json_recovery import recover_json

SYSTEM_PROMPT = """You are a recruitment fraud behavior analyst.

Analyze the provided recruiter communication for behavioral fraud signals.

You MUST return ONLY a JSON object (no markdown, no preamble):
{
  "signals": ["list of specific behavioral signals found"],
  "risk_score": <integer 0-100>,
  "reasoning": "<1-3 sentence explanation>",
  "safe_indicators": ["list of reassuring/legitimate signals found"]
}

HIGH RISK behaviors (each adds significant risk):
- Payment or deposit requested before or during onboarding
- Telegram-only or WhatsApp-only contact for hiring
- Interview step skipped entirely
- Extreme urgency ("reply in 24h or lose the offer")
- Crypto or UPI payment requested
- Refundable fee framing
- Work-from-home equipment purchase required
- Unsolicited job offers with no application

SAFE signals (reduce risk):
- Official corporate email domains (e.g., @google.com, @microsoft.com)
- Standard multi-round interview process
- No payment mentioned at all
- Reference to official job boards (LinkedIn, careers.company.com)
- Standard onboarding with HR department

Be calibrated. Do NOT flag safe, normal hiring flows as risky.
Risk score 0-20: LOW. 21-50: MEDIUM. 51-75: HIGH. 76-100: CRITICAL."""


def run(text: str) -> dict:
    """Run behavior analysis on provided text. Returns analysis dict."""
    start = time.time()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this recruiter communication:\n\n{text}"},
    ]

    try:
        raw = reason(messages, max_tokens=800)
        parsed = recover_json(raw)
        if not parsed:
            return {
                "signals": ["Unable to parse behavior analysis"],
                "risk_score": 30,
                "reasoning": "Analysis output could not be parsed.",
                "safe_indicators": [],
                "provider": nvidia_model(),
                "latency_ms": int((time.time() - start) * 1000),
                "error": "json_parse_failed",
            }
        parsed["provider"] = nvidia_model()
        parsed["latency_ms"] = int((time.time() - start) * 1000)
        return parsed
    except RuntimeError as e:
        fallback = _heuristic_behavior(text)
        fallback.update(
            {
                "provider": f"local_heuristic_after_{nvidia_model()}_failure",
                "latency_ms": int((time.time() - start) * 1000),
                "error": str(e),
            }
        )
        return fallback


def _heuristic_behavior(text: str) -> dict:
    lowered = text.lower()
    signals = []
    safe_indicators = []

    checks = [
        ("payment_or_deposit_request", any(term in lowered for term in ["deposit", "security fee", "registration fee", "refundable", "upi", "pay "])),
        ("telegram_or_whatsapp_onboarding", "telegram" in lowered or "whatsapp" in lowered),
        ("interview_bypassed", any(term in lowered for term in ["no interview", "without interview", "direct selection", "selected for"])),
        ("urgency_pressure", any(term in lowered for term in ["within 24", "urgent", "limited slots", "reply immediately"])),
        ("suspicious_internship_terms", "internship" in lowered and any(term in lowered for term in ["task", "certificate", "offer letter", "virtual"])),
    ]
    for name, matched in checks:
        if matched:
            signals.append(name)

    if any(term in lowered for term in ["no fees", "no payment", "official careers", "interview"]):
        safe_indicators.append("standard_or_no_fee_hiring_language")

    risk = min(95, 15 + len(signals) * 18)
    if "payment_or_deposit_request" in signals:
        risk = max(risk, 70)
    if "telegram_or_whatsapp_onboarding" in signals and "payment_or_deposit_request" in signals:
        risk = max(risk, 88)

    return {
        "signals": signals,
        "risk_score": risk if signals else 35,
        "reasoning": "Deterministic fallback used because the primary behavior model failed. Risk is estimated from payment, channel, interview, urgency, and internship-pattern signals.",
        "safe_indicators": safe_indicators,
    }
