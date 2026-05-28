"""
OSINT Agent — checks company legitimacy, onboarding behavior, recruiter claims.
Uses NVIDIA NIM for reasoning.

Key upgrade: Extracts company name from evidence text and injects it into the
prompt so the model can reason specifically about whether this *particular* company
is known to run fake internships, even if it is a registered entity.
"""

import re
import time
from providers.nvidia_client import reason, model_name as nvidia_model
from utils.json_recovery import recover_json

SYSTEM_PROMPT = """You are a senior OSINT analyst specializing in recruitment fraud and internship scam investigation.

CRITICAL RULE: Do NOT clear a company just because it is registered, incorporated, or has a real website.
Registered companies are frequently used as fronts for:
 - Fake internship programs with UPI/deposit requirements
 - Scam offer letters impersonating the real company
 - Telegram-only onboarding with no real HR involvement
 - Unpaid or exploitative internships advertised with inflated claims

Analyze the recruiter communication and extracted company name for:
1. Company legitimacy signals — does the communication match how the REAL company hires?
2. Onboarding behavior — standard (multi-round interview, official email, contract) or suspicious (task-based, Telegram, fee)?
3. Recruiter credibility — does the recruiter's profile, email domain, and language match the claimed company?
4. Internship red flags — unpaid stipend after fee, certificate-for-task scams, vague role descriptions
5. Communication quality — professional vs. template-spam, grammar issues, pressure tactics

Return ONLY a JSON object:
{
  "company_name": "<extracted company name or Unknown>",
  "company_legitimacy": "<assessment — REAL_AND_MATCHES | REAL_BUT_SUSPICIOUS | IMPERSONATION | UNKNOWN>",
  "onboarding_assessment": "<standard | suspicious | highly_suspicious>",
  "recruiter_credibility": "<credible | questionable | not_credible>",
  "internship_flags": ["specific flag found"],
  "risk_score": <integer 0-100>,
  "key_findings": ["finding 1", "finding 2"],
  "reasoning": "<2-3 sentence summary — be specific about what was found>"
}

Risk calibration:
- 0-20: LOW — standard corporate hiring, official channels, no red flags
- 21-50: MEDIUM — some unusual patterns but plausible
- 51-75: HIGH — multiple fraud indicators
- 76-100: CRITICAL — clear scam pattern (deposit, Telegram-only, impersonation)

Never give a LOW score when fees, UPI payments, or Telegram-only contact are present."""


def _extract_company_hint(text: str) -> str:
    """Best-effort company name extraction from evidence text."""
    patterns = [
        r"company(?:\s*name)?[:\-]\s*([A-Za-z0-9][A-Za-z0-9 .,&'-]{1,60})",
        r"from\s+([A-Z][A-Za-z0-9][A-Za-z0-9 .,&'-]{1,50}?)[\s,.]",
        r"internship\s+at\s+([A-Z][A-Za-z0-9][A-Za-z0-9 .,&'-]{1,50})",
        r"offer\s+(?:from|by)\s+([A-Z][A-Za-z0-9][A-Za-z0-9 .,&'-]{1,50})",
        r"team\s+at\s+([A-Z][A-Za-z0-9][A-Za-z0-9 .,&'-]{1,50})",
        r"([A-Z][A-Za-z0-9][A-Za-z0-9 .,&'-]{1,40})\s+(?:Pvt\.?\s*Ltd|Private\s+Limited|Technologies|Tech\b|Solutions|Services|Consulting)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            candidate = m.group(1).strip().strip(".,")
            if 2 < len(candidate) < 80:
                return candidate
    return "Unknown"


def run(text: str) -> dict:
    """Run OSINT analysis. Returns analysis dict."""
    start = time.time()

    company_hint = _extract_company_hint(text)
    company_context = (
        f"\n\nExtracted company name: {company_hint}\n"
        "Investigate whether THIS specific company is known to run fake internships, "
        "scam offer letters, or deposit-based recruitment fraud."
        if company_hint != "Unknown"
        else ""
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Investigate this recruiter communication:{company_context}\n\n{text}"
            ),
        },
    ]

    try:
        raw = reason(messages, max_tokens=900)
        parsed = recover_json(raw)
        if not parsed:
            return {
                "company_name": company_hint,
                "company_legitimacy": "Unknown — parse failed",
                "onboarding_assessment": "Unknown",
                "recruiter_credibility": "Unknown",
                "internship_flags": [],
                "risk_score": 35,
                "key_findings": ["Analysis output could not be parsed"],
                "reasoning": "OSINT analysis output could not be parsed.",
                "provider": nvidia_model(),
                "latency_ms": int((time.time() - start) * 1000),
                "error": "json_parse_failed",
            }
        # Ensure company_name is present
        if not parsed.get("company_name") and company_hint != "Unknown":
            parsed["company_name"] = company_hint
        parsed["provider"] = nvidia_model()
        parsed["latency_ms"] = int((time.time() - start) * 1000)
        return parsed
    except RuntimeError as e:
        return {
            "company_name": company_hint,
            "company_legitimacy": "Unknown",
            "onboarding_assessment": "Unknown",
            "recruiter_credibility": "Unknown",
            "internship_flags": [],
            "risk_score": 0,
            "key_findings": [],
            "reasoning": f"OSINT agent failed: {e}",
            "provider": nvidia_model(),
            "latency_ms": int((time.time() - start) * 1000),
            "error": str(e),
        }
