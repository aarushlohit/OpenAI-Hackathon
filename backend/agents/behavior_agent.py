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
        return {
            "signals": [],
            "risk_score": 0,
            "reasoning": f"Behavior agent failed: {e}",
            "safe_indicators": [],
            "provider": nvidia_model(),
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }
