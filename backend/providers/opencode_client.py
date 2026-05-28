"""OpenCode handoff for web reputation checks and final scam conclusion."""

import json
import os
import subprocess
from typing import Any

try:
    from utils.json_recovery import recover_json
except ModuleNotFoundError:
    from backend.utils.json_recovery import recover_json

OPENCODE_MODEL = os.getenv("OPENCODE_MODEL", "opencode/deepseek-v4-flash-free")
OPENCODE_TIMEOUT_SECONDS = int(os.getenv("OPENCODE_TIMEOUT_SECONDS", "120"))


def search_company_reputation(evidence: dict[str, Any]) -> dict[str, Any]:
    """
    Use OpenCode web search to validate the company/internship beyond registration status.

    This intentionally asks for Glassdoor, AmbitionBox, Reddit, and scam-report searches
    because a registered company can still run fake internships, deposit schemes, or
    impersonated onboarding.
    """
    prompt = f"""You are a web-search OSINT investigator for internship and recruitment scams.

Use web search. Do NOT stop at "company is registered" or "company exists".
A real registered company can still be linked to scam internships, fake recruiters, deposit fraud,
unpaid internship complaints, impersonation, or bait-and-switch onboarding.

Search and compare evidence from:
- Glassdoor reviews/interview pages: site:glassdoor.com OR site:glassdoor.co.in
- AmbitionBox reviews/interviews/salaries: site:ambitionbox.com
- Reddit complaints/discussions: site:reddit.com company internship scam OR offer letter OR fraud
- Public scam warnings: company name + scam, fraud, internship scam, offer letter scam, UPI deposit
- Domain/recruiter evidence: suspicious domains, emails, Telegram handles, payment requests

Return ONLY valid JSON:
{{
  "search_performed": true,
  "conclusion": "SCAM | NOT SCAM | UNCERTAIN",
  "confidence": 0,
  "company": "company name or Unknown",
  "registered_but_suspicious": false,
  "sources_checked": [
    {{"source": "Glassdoor", "status": "found | not_found | blocked | conflicting", "finding": "...", "url_or_query": "..."}},
    {{"source": "AmbitionBox", "status": "found | not_found | blocked | conflicting", "finding": "...", "url_or_query": "..."}},
    {{"source": "Reddit", "status": "found | not_found | blocked | conflicting", "finding": "...", "url_or_query": "..."}},
    {{"source": "Scam reports/web", "status": "found | not_found | blocked | conflicting", "finding": "...", "url_or_query": "..."}}
  ],
  "reputation_signals": ["specific public reputation signal"],
  "scam_signals": ["specific scam signal from public web or evidence"],
  "safe_signals": ["specific legitimacy signal"],
  "summary": "2-4 sentence web-search conclusion",
  "recommended_action": "what the user should do next"
}}

Evidence to investigate:
{json.dumps(evidence, ensure_ascii=False, indent=2)}
"""
    result = _run_opencode_prompt(prompt)
    result["stage"] = "web_reputation"
    return result


def assess_offer_letter(evidence: dict[str, Any]) -> dict[str, Any]:
    """Run `opencode run "prompt" -m opencode/deepseek-v4-flash-free` and parse the result."""
    prompt = f"""You are a recruitment scam investigator.

Review this extracted offer-letter/company evidence and web-search reputation evidence.
Do not mark an internship safe just because a company appears registered.
Payment/deposit requests, Telegram-only onboarding, domain impersonation, bad public reviews,
or Reddit/AmbitionBox/Glassdoor complaints must outweigh basic registration.

Return ONLY valid JSON:
{{
  "conclusion": "SCAM | NOT SCAM | UNCERTAIN",
  "confidence": 0,
  "company": "company name or Unknown",
  "summary": "one paragraph conclusion",
  "key_evidence": ["evidence point"],
  "recommended_action": "what the user should do next"
}}

Evidence:
{json.dumps(evidence, ensure_ascii=False, indent=2)}
"""

    return _run_opencode_prompt(prompt)


def _run_opencode_prompt(prompt: str) -> dict[str, Any]:
    cmd = ["opencode", "run", prompt, "-m", OPENCODE_MODEL]
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=OPENCODE_TIMEOUT_SECONDS,
            check=False,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
    except FileNotFoundError:
        return {
            "provider": OPENCODE_MODEL,
            "error": "opencode command not found",
            "command": f'opencode run "<prompt>" -m {OPENCODE_MODEL}',
        }
    except subprocess.TimeoutExpired:
        return {
            "provider": OPENCODE_MODEL,
            "error": f"opencode timed out after {OPENCODE_TIMEOUT_SECONDS}s",
            "command": f'opencode run "<prompt>" -m {OPENCODE_MODEL}',
        }

    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
    parsed = recover_json(output)
    result = parsed if parsed else {"raw_response": output}
    result["provider"] = OPENCODE_MODEL
    result["exit_code"] = completed.returncode
    result["command"] = f'opencode run "<prompt>" -m {OPENCODE_MODEL}'
    return result
