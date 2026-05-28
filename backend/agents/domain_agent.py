"""
Domain Agent — deterministic domain intelligence.
Uses tldextract + rapidfuzz (NO LLM for core logic).
LLM is used only for contextual summary.
"""

import time
from utils.domain_validator import analyze_domains_in_text


def run(text: str) -> dict:
    """
    Run domain analysis on text.
    Returns analysis dict with extracted domains and risk assessment.
    """
    start = time.time()

    domain_analyses = analyze_domains_in_text(text)

    if not domain_analyses:
        return {
            "domains_found": [],
            "risk_score": 5,
            "highest_risk_domain": None,
            "summary": "No domains or URLs found in the provided text.",
            "latency_ms": int((time.time() - start) * 1000),
        }

    # Calculate aggregate risk from domain scores
    max_delta = max(d["score_delta"] for d in domain_analyses)
    total_delta = sum(d["score_delta"] for d in domain_analyses)

    # Base risk: 10 (neutral). Max out at 95.
    base = 10
    risk_score = min(95, max(0, base + max_delta + (total_delta // 3)))

    # Find the highest-risk domain
    highest = max(domain_analyses, key=lambda d: d["score_delta"])

    # Aggregate all signals
    all_signals = []
    for d in domain_analyses:
        all_signals.extend(d["signals"])

    # Build summary
    domains_str = ", ".join(d["domain"] for d in domain_analyses)
    if risk_score >= 75:
        summary = f"CRITICAL domain risk detected. Domains found: {domains_str}. {'; '.join(all_signals[:3])}"
    elif risk_score >= 40:
        summary = f"Suspicious domain patterns found in: {domains_str}. {'; '.join(all_signals[:2])}"
    else:
        summary = f"Domains appear legitimate: {domains_str}."

    return {
        "domains_found": [
            {
                "domain": d["domain"],
                "risk_level": d["risk_level"],
                "signals": d["signals"],
            }
            for d in domain_analyses
        ],
        "risk_score": risk_score,
        "highest_risk_domain": highest["domain"] if highest else None,
        "all_signals": all_signals,
        "summary": summary,
        "latency_ms": int((time.time() - start) * 1000),
        "provider": "deterministic (tldextract + rapidfuzz)",
    }
