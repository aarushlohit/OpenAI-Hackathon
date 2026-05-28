"""
Domain validation and typo-squatting detection.
Uses tldextract + rapidfuzz for deterministic analysis.
"""

import re
import tldextract
from rapidfuzz import fuzz

# Known legitimate corporate domains (registered domain without TLD)
LEGITIMATE_DOMAINS = [
    "google", "microsoft", "amazon", "apple", "meta", "netflix", "linkedin",
    "twitter", "x", "github", "gitlab", "dropbox", "salesforce", "oracle",
    "ibm", "adobe", "nvidia", "intel", "qualcomm", "spotify", "uber", "lyft",
    "airbnb", "stripe", "twilio", "slack", "zoom", "atlassian", "jira",
    "hubspot", "shopify", "paypal", "square", "robinhood", "coinbase",
    "deloitte", "accenture", "mckinsey", "bcg", "pwc", "kpmg", "ey",
    "wipro", "infosys", "tcs", "hcl", "cognizant", "capgemini",
    "wells", "jpmorgan", "citibank", "barclays", "goldmansachs",
    "tesla", "spacex", "openai", "anthropic", "deepmind",
]

# TLDs that are almost never used by legitimate enterprises
SUSPICIOUS_TLDS = {
    "xyz", "tk", "ml", "ga", "cf", "gq", "top", "click", "loan", "download",
    "stream", "science", "party", "review", "trade", "win", "racing", "bid",
    "men", "ninja", "date", "faith", "accountant", "online", "site", "website",
    "space", "tech", "fun", "host", "pw", "buzz", "club", "monster", "link",
    "life", "network", "center", "info",  # "info" is marginal
}

# High-legitimacy TLDs
TRUSTED_TLDS = {"com", "org", "net", "edu", "gov", "io", "co"}


def extract_domains_from_text(text: str) -> list[str]:
    """Extract all URLs / domain patterns from text."""
    pattern = r"(?:https?://)?(?:www\.)?([a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)+)"
    matches = re.findall(pattern, text)
    return list(set(matches))


def analyze_domain(domain: str) -> dict:
    """
    Analyze a single domain string for legitimacy.
    Returns a dict with: domain, risk_level, reason, score_delta
    score_delta is positive = INCREASE risk, negative = DECREASE risk.
    """
    ext = tldextract.extract(domain)
    registered = ext.domain.lower()
    tld = ext.suffix.lower()
    full_domain = f"{registered}.{tld}"

    result = {
        "domain": domain,
        "registered": registered,
        "tld": tld,
        "risk_level": "low",
        "signals": [],
        "score_delta": 0,
    }

    # 1. Suspicious TLD
    if tld in SUSPICIOUS_TLDS:
        result["signals"].append(f"Suspicious TLD (.{tld}) — rarely used by legitimate companies")
        result["score_delta"] += 35
        result["risk_level"] = "high"

    # 2. Trusted TLD
    if tld in TRUSTED_TLDS and result["score_delta"] == 0:
        result["score_delta"] -= 10

    # 3. Typo-squatting check against known legitimate domains
    best_match = None
    best_score = 0
    for legit in LEGITIMATE_DOMAINS:
        score = fuzz.ratio(registered, legit)
        if score > best_score:
            best_score = score
            best_match = legit

    if best_match:
        if registered == best_match:
            # Exact match on registered domain — likely legit
            result["signals"].append(f"Domain matches known legitimate company: {best_match}")
            result["score_delta"] -= 20
        elif best_score >= 85 and registered != best_match:
            # Close but not exact — typo squat
            result["signals"].append(
                f"Possible typo-squat of '{best_match}' (similarity {best_score:.0f}%) — CRITICAL fraud indicator"
            )
            result["score_delta"] += 50
            result["risk_level"] = "critical"

    # 4. Leetspeak / character substitution (0->o, 3->e, 1->i, etc.)
    leet_normalized = (
        registered
        .replace("0", "o")
        .replace("3", "e")
        .replace("1", "i")
        .replace("@", "a")
        .replace("5", "s")
        .replace("4", "a")
    )
    if leet_normalized != registered:
        for legit in LEGITIMATE_DOMAINS:
            score = fuzz.ratio(leet_normalized, legit)
            if score >= 85:
                result["signals"].append(
                    f"Leetspeak substitution detected — '{registered}' normalizes to '{leet_normalized}' "
                    f"matching '{legit}' — CRITICAL typo-squat"
                )
                result["score_delta"] += 60
                result["risk_level"] = "critical"
                break

    # 5. Hyphenated company name with keywords
    if "-" in registered:
        parts = registered.split("-")
        for legit in LEGITIMATE_DOMAINS:
            if legit in parts:
                suspicious_keywords = ["careers", "jobs", "apply", "hire", "recruit", "onboard", "offer"]
                other_parts = [p for p in parts if p != legit]
                if any(kw in other_parts for kw in suspicious_keywords):
                    result["signals"].append(
                        f"Hyphenated domain uses '{legit}' brand with recruitment keywords — high fraud risk"
                    )
                    result["score_delta"] += 45
                    result["risk_level"] = "critical"
                    break

    if not result["signals"]:
        result["signals"].append(f"Domain appears legitimate ({full_domain})")

    return result


def analyze_domains_in_text(text: str) -> list[dict]:
    """Extract and analyze all domains found in text."""
    domains = extract_domains_from_text(text)
    return [analyze_domain(d) for d in domains]
