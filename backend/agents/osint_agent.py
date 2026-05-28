"""
OSINT Agent — checks company legitimacy, onboarding behavior, recruiter claims.
Uses NVIDIA NIM for reasoning.
"""

import time
from providers.nvidia_client import reason, model_name as nvidia_model
from utils.json_recovery import recover_json

SYSTEM_PROMPT = """You are an OSINT analyst specializing in recruitment fraud investigation.

Given recruiter communication, analyze:
1. Company legitimacy signals (does this seem like a real, known company?)
2. Onboarding behavior (is the process standard or suspicious?)
3. Recruiter claims (are they plausible for the claimed company/role?)
4. Communication patterns (professional or rushed/informal?)

Return ONLY a JSON object:
{
  "company_legitimacy": "<assessment of whether the company appears real>",
  "onboarding_assessment": "<assessment of onboarding process>",
  "recruiter_credibility": "<assessment of recruiter claims>",
  "risk_score": <integer 0-100>,
  "key_findings": ["finding 1", "finding 2"],
  "reasoning": "<2-3 sentence summary>"
}

Be balanced. Many legitimate companies recruit via LinkedIn, email, and phone.
Flag only genuine red flags — not common recruiting practices.

Risk score 0-20: LOW. 21-50: MEDIUM. 51-75: HIGH. 76-100: CRITICAL."""


def run(text: str) -> dict:
    """Run OSINT analysis. Returns analysis dict."""
    start = time.time()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Investigate this recruiter communication:\n\n{text}"},
    ]

    try:
        raw = reason(messages, max_tokens=800)
        parsed = recover_json(raw)
        if not parsed:
            return {
                "company_legitimacy": "Unknown — parse failed",
                "onboarding_assessment": "Unknown",
                "recruiter_credibility": "Unknown",
                "risk_score": 30,
                "key_findings": ["Analysis output could not be parsed"],
                "reasoning": "OSINT analysis output could not be parsed.",
                "provider": nvidia_model(),
                "latency_ms": int((time.time() - start) * 1000),
                "error": "json_parse_failed",
            }
        parsed["provider"] = nvidia_model()
        parsed["latency_ms"] = int((time.time() - start) * 1000)
        return parsed
    except RuntimeError as e:
        return {
            "company_legitimacy": "Unknown",
            "onboarding_assessment": "Unknown",
            "recruiter_credibility": "Unknown",
            "risk_score": 0,
            "key_findings": [],
            "reasoning": f"OSINT agent failed: {e}",
            "provider": nvidia_model(),
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }
