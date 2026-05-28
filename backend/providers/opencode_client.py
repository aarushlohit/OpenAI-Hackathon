"""OpenCode API handoff for web reputation checks and final scam conclusion."""

import json
import os
import re
import urllib.parse
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

try:
    from utils.json_recovery import recover_json
except ModuleNotFoundError:
    from backend.utils.json_recovery import recover_json

OPENCODE_MODEL = os.getenv("OPENCODE_MODEL", "opencode/deepseek-v4-flash-free")
OPENCODE_API_MODEL = os.getenv(
    "OPENCODE_API_MODEL",
    OPENCODE_MODEL.removeprefix("opencode/"),
)
OPENCODE_API_URL = os.getenv(
    "OPENCODE_API_URL",
    "https://opencode.ai/zen/v1/chat/completions",
)
OPENCODE_TIMEOUT_SECONDS = int(os.getenv("OPENCODE_TIMEOUT_SECONDS", "90"))
SEARCH_TIMEOUT_SECONDS = int(os.getenv("REPUTATION_SEARCH_TIMEOUT_SECONDS", "12"))


def search_company_reputation(evidence: dict[str, Any]) -> dict[str, Any]:
    """
    Use OpenCode web search to validate the company/internship beyond registration status.

    A registered company can still run fake internships, deposit schemes, or impersonated
    onboarding. We search Glassdoor, AmbitionBox, Reddit, Quora, and generic scam-report
    queries and pass the actual page snippets to the LLM so it has real grounding.
    """
    search_results = _search_public_reputation(evidence)
    enriched_evidence = {**evidence, "public_search_results": search_results}

    # Build a concise snippet summary to inject into the prompt
    snippet_summary = _summarize_search_snippets(search_results)

    prompt = f"""You are a senior OSINT investigator specialising in internship and recruitment scams.

--- CRITICAL RULES ---
1. "Company is registered" or "company has a website" is NOT sufficient evidence of legitimacy.
   Scammers routinely use real registered companies as fronts for fake internships.
2. A company that appears on Glassdoor or AmbitionBox with mostly positive reviews can STILL be
   running a separate scam internship campaign. Look for recent complaints specifically about
   internships, offer letters, UPI payments, or Telegram onboarding.
3. If the public search snippets show ANY credible complaint about the company asking for deposits,
   UPI, or certificate-based scam internships, escalate to SCAM or at minimum UNCERTAIN.
4. Absence of results ("not_found") on Reddit or scam-report sites is weak evidence of legitimacy;
   do NOT treat it as a strong safe signal.

--- REAL-WORLD WEB SEARCH SNIPPETS ---
{snippet_summary}

--- INSTRUCTIONS ---
Synthesize all evidence (web snippets + document/domain/behavioral evidence below).
Pay special attention to:
 - Reddit posts, Quora answers, or review-site entries mentioning scam, fraud, deposit, UPI,
   certificate, offer letter, or Telegram for THIS company.
 - Whether the onboarding described matches how legitimate companies in this sector actually hire.
 - Domain mismatches, informal email addresses, missing official contact details.

Return ONLY valid JSON:
{{
  "search_performed": true,
  "conclusion": "SCAM | NOT SCAM | UNCERTAIN",
  "confidence": <integer 0-100>,
  "company": "company name or Unknown",
  "registered_but_suspicious": <true|false>,
  "sources_checked": [
    {{"source": "Glassdoor", "status": "found | not_found | blocked | conflicting", "finding": "<what was found or not found>", "url_or_query": "<query used>"}},
    {{"source": "AmbitionBox", "status": "found | not_found | blocked | conflicting", "finding": "<what was found or not found>", "url_or_query": "<query used>"}},
    {{"source": "Reddit", "status": "found | not_found | blocked | conflicting", "finding": "<what was found or not found>", "url_or_query": "<query used>"}},
    {{"source": "Quora", "status": "found | not_found | blocked | conflicting", "finding": "<what was found or not found>", "url_or_query": "<query used>"}},
    {{"source": "Scam reports/web", "status": "found | not_found | blocked | conflicting", "finding": "<what was found or not found>", "url_or_query": "<query used>"}}
  ],
  "reputation_signals": ["specific public reputation signal found in web snippets"],
  "scam_signals": ["specific scam signal found in web snippets or evidence — be explicit"],
  "safe_signals": ["specific legitimacy signal"],
  "summary": "3-5 sentence web-search conclusion — cite specific snippets or absence of results",
  "recommended_action": "clear 1-2 sentence advice for the user"
}}

Full evidence bundle:
{json.dumps(enriched_evidence, ensure_ascii=False, indent=2)}
"""
    result = _run_opencode_prompt(prompt)
    if result.get("error") or (not result.get("conclusion") and not result.get("sources_checked")):
        fallback = _fallback_reputation(enriched_evidence)
        fallback["provider"] = result.get("provider", OPENCODE_MODEL)
        fallback["api_model"] = result.get("api_model", OPENCODE_API_MODEL)
        fallback["api_url"] = result.get("api_url", OPENCODE_API_URL)
        if result.get("error"):
            fallback["opencode_error"] = result["error"]
        result = fallback
    elif search_results:
        result["public_search_results"] = search_results
    result["stage"] = "web_reputation"
    return result


def assess_offer_letter(evidence: dict[str, Any]) -> dict[str, Any]:
    """Run OpenCode's OpenAI-compatible HTTP API and parse the final result."""
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

    result = _run_opencode_prompt(prompt)
    if result.get("error") or not result.get("conclusion"):
        result.update(_fallback_assessment(evidence))
    return result


def _run_opencode_prompt(prompt: str) -> dict[str, Any]:
    api_key = os.getenv("OPENCODE_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return {
            "provider": OPENCODE_MODEL,
            "error": "OPENCODE_API_KEY or OPENROUTER_API_KEY is not set",
            "api_url": OPENCODE_API_URL,
        }

    payload = {
        "model": OPENCODE_API_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": int(os.getenv("OPENCODE_MAX_TOKENS", "4096")),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            OPENCODE_API_URL,
            headers=headers,
            json=payload,
            timeout=OPENCODE_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        message = data["choices"][0]["message"]
        output = message.get("content") or ""
        if not output:
            output = message.get("reasoning_content") or ""
    except requests.HTTPError as exc:
        body = exc.response.text[:500] if exc.response is not None else ""
        return {
            "provider": OPENCODE_MODEL,
            "error": f"OpenCode API HTTP error {exc.response.status_code if exc.response else 'unknown'}: {body}",
            "api_url": OPENCODE_API_URL,
        }
    except requests.RequestException as exc:
        return {
            "provider": OPENCODE_MODEL,
            "error": f"OpenCode API request failed: {exc}",
            "api_url": OPENCODE_API_URL,
        }
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        return {
            "provider": OPENCODE_MODEL,
            "error": f"OpenCode API response could not be parsed: {exc}",
            "api_url": OPENCODE_API_URL,
        }

    parsed = recover_json(output)
    result = parsed if parsed else {"raw_response": output}
    if not output:
        result["error"] = "OpenCode API returned an empty assistant message"
    result["provider"] = OPENCODE_MODEL
    result["api_model"] = OPENCODE_API_MODEL
    result["api_url"] = OPENCODE_API_URL
    return result


def _flatten_evidence(evidence: dict[str, Any]) -> str:
    return json.dumps(evidence, ensure_ascii=False).lower()


def _extract_company_from_evidence(evidence: dict[str, Any]) -> str:
    image = evidence.get("image_extraction")
    if isinstance(image, dict) and image.get("company_name"):
        return str(image["company_name"])
    for value in evidence.values():
        if isinstance(value, dict) and value.get("company"):
            return str(value["company"])
    text = str(evidence.get("text") or "")
    match = re.search(r"\b(?:company|from)\s*[:\-]\s*([A-Za-z0-9 .&-]{2,60})", text, re.I)
    return match.group(1).strip() if match else "Unknown"


def _search_public_reputation(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    company = _extract_company_from_evidence(evidence)
    if company == "Unknown":
        return []

    queries = [
        ("Glassdoor", f'"{company}" internship site:glassdoor.com OR site:glassdoor.co.in'),
        ("AmbitionBox", f'"{company}" internship site:ambitionbox.com reviews'),
        ("Reddit", f'"{company}" internship scam OR fraud OR "offer letter" site:reddit.com'),
        ("Quora", f'"{company}" internship scam OR legit OR fake site:quora.com'),
        ("Scam reports/web", f'"{company}" internship scam fraud UPI deposit "offer letter" certificate -site:linkedin.com'),
    ]
    results: list[dict[str, Any]] = []
    for source, query in queries:
        results.append(_duckduckgo_search(source, query))
    return results


def _duckduckgo_search(source: str, query: str) -> dict[str, Any]:
    url = "https://r.jina.ai/http://duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    try:
        response = requests.get(url, timeout=SEARCH_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        return {
            "source": source,
            "status": "blocked",
            "query": query,
            "finding": f"Search request failed: {exc}",
            "snippet": "",
            "results": [],
        }

    raw_text = response.text

    # Extract up to 3 result links
    results = []
    for title, link in re.findall(r"## \[(.*?)\]\((.*?)\)", raw_text):
        clean_link = _clean_duckduckgo_link(link)
        if clean_link and "duckduckgo.com" not in clean_link:
            results.append({"title": title.strip(), "url": clean_link})
        if len(results) >= 4:
            break

    # Extract a meaningful text snippet (first 1200 chars of rendered body)
    body_text = re.sub(r"\[.*?\]\(.*?\)", "", raw_text)  # remove markdown links
    body_text = re.sub(r"[#>*_`|]+", " ", body_text)      # strip markdown symbols
    body_text = re.sub(r"\s{2,}", " ", body_text).strip()
    snippet = body_text[:1200] if body_text else ""

    status = "found" if results else "not_found"
    finding = (
        f"Found {len(results)} public result(s) for {source}."
        if results
        else f"No clear public results found for {source}."
    )
    return {
        "source": source,
        "status": status,
        "query": query,
        "finding": finding,
        "snippet": snippet,
        "results": results,
    }


def _clean_duckduckgo_link(link: str) -> str:
    parsed = urllib.parse.urlparse(link)
    qs = urllib.parse.parse_qs(parsed.query)
    target = qs.get("uddg", [link])[0]
    return urllib.parse.unquote(target)


def _summarize_search_snippets(search_results: list[dict[str, Any]]) -> str:
    """Build a concise text block of search snippets to inject into the LLM prompt."""
    if not search_results:
        return "No public search results were retrieved."
    parts = []
    for item in search_results:
        source = item.get("source", "Unknown")
        status = item.get("status", "unknown")
        query = item.get("query", "")
        snippet = (item.get("snippet") or "").strip()[:600]
        links = item.get("results", [])
        link_titles = "; ".join(r.get("title", "") for r in links[:3])
        block = f"[{source}] status={status} | query: {query}"
        if link_titles:
            block += f"\n  Top results: {link_titles}"
        if snippet:
            block += f"\n  Snippet: {snippet}"
        parts.append(block)
    return "\n\n".join(parts)


def _has_positive_payment_signal(text: str, term: str) -> bool:
    if re.search(rf"\b(no|without|not|never)\s+(?:\w+\s+){{0,3}}{re.escape(term)}\b", text):
        return False
    if re.search(rf"\b{re.escape(term)}\s+(?:is\s+)?(?:not|required|requested|needed)\b", text):
        return False
    return term in text


def _fallback_reputation(evidence: dict[str, Any]) -> dict[str, Any]:
    text = _flatten_evidence(evidence)
    scam_terms = ["upi", "telegram", "whatsapp", "no interview", "refundable", ".xyz"]
    safe_terms = ["no payment", "no deposit", "official", "codsoft.in", "contact@"]
    scam_hits = [term for term in scam_terms if term in text]
    if _has_positive_payment_signal(text, "deposit"):
        scam_hits.append("deposit")
    if _has_positive_payment_signal(text, "payment"):
        scam_hits.append("payment")
    safe_hits = [term for term in safe_terms if term in text]
    public_results = evidence.get("public_search_results") if isinstance(evidence, dict) else None
    found_sources = [
        item for item in public_results or []
        if isinstance(item, dict) and item.get("status") == "found"
    ]
    conclusion = "SCAM" if len(scam_hits) >= 2 else "UNCERTAIN" if scam_hits else "NOT SCAM"
    return {
        "search_performed": bool(public_results),
        "conclusion": conclusion,
        "confidence": 68 if scam_hits else 55,
        "registered_but_suspicious": bool(scam_hits and safe_hits),
        "sources_checked": public_results or [
            {
                "source": "Reputation fallback",
                "status": "degraded",
                "finding": "Public search results were unavailable; deterministic evidence fallback was used.",
                "url_or_query": "Glassdoor, AmbitionBox, Reddit, scam-report queries not completed",
            }
        ],
        "reputation_signals": safe_hits,
        "scam_signals": scam_hits,
        "safe_signals": safe_hits,
        "summary": (
            f"Public search returned {len(found_sources)} source group(s), but OpenCode did not produce a complete reputation JSON. "
            "The conclusion was estimated from the search snippets, extracted offer text, and recruitment scam patterns."
        ),
    }


def _fallback_assessment(evidence: dict[str, Any]) -> dict[str, Any]:
    text = _flatten_evidence(evidence)
    scam_hits = [
        term for term in ["upi", "telegram", "whatsapp", "no interview", "refundable", ".xyz"]
        if term in text
    ]
    if _has_positive_payment_signal(text, "deposit"):
        scam_hits.append("deposit")
    if _has_positive_payment_signal(text, "payment"):
        scam_hits.append("payment")
    safe_hits = [term for term in ["no payment", "no deposit", "official", "contact@", "website"] if term in text]
    conclusion = "SCAM" if len(scam_hits) >= 2 else "UNCERTAIN" if scam_hits else "NOT SCAM"
    return {
        "conclusion": conclusion,
        "confidence": 72 if scam_hits else 58,
        "company": _extract_company(evidence),
        "summary": "Final OpenCode output was unavailable; deterministic final assessment was computed from extracted offer text, domain signals, and agent findings.",
        "key_evidence": scam_hits or safe_hits,
        "recommended_action": (
            "Do not pay fees or continue off-platform onboarding. Verify through the company's official website and email."
            if scam_hits
            else "Verify the internship directly through official company channels before sharing documents."
        ),
    }


def _extract_company(evidence: dict[str, Any]) -> str:
    image = evidence.get("image_extraction")
    if isinstance(image, dict) and image.get("company_name"):
        return str(image["company_name"])
    web = evidence.get("web_reputation")
    if isinstance(web, dict) and web.get("company"):
        return str(web["company"])
    return "Unknown"
