"""Web Search Agent — domain verification and company legitimacy intelligence.

Uses OpenCode runtime (via subprocess + PTY, matching the v3.py pattern) to perform
real web searches verifying company domains, careers portals, recruiter email domains,
and onboarding legitimacy against public web sources.

This agent REDUCES suspicion when:
- Official corporate domain ownership confirmed
- Company careers page validates onboarding flow
- Recruiter email matches verified domain
- No payment-before-onboarding patterns found on official page

This agent RAISES suspicion when:
- Domain not found / newly registered
- No official careers portal
- Recruiter domain does not match company domain
- Page has known scam indicators
"""

import asyncio
import json
import logging
import os
import pty
import re
import select
import subprocess
import sys
from time import perf_counter
from typing import Any

from app.agents.base import AgentContext, InvestigationAgent
from app.models.web_search_result import WebSearchResult
from app.schemas.investigation import InvestigationRequest

logger = logging.getLogger(__name__)


def _console_log(message: str) -> None:
    print(f"[WEB_SEARCH] {message}", file=sys.stderr, flush=True)


# Known legitimate company domain patterns — official domains get fast trust pass
_VERIFIED_COMPANY_DOMAINS: set[str] = {
    "google.com", "employee.google.com", "careers.google.com",
    "microsoft.com", "careers.microsoft.com",
    "amazon.com", "amazon.jobs",
    "meta.com", "linkedin.com",
    "apple.com", "jobs.apple.com",
    "netflix.com", "jobs.netflix.com",
    "nvidia.com", "infosys.com", "wipro.com", "tcs.com",
    "hcl.com", "accenture.com", "ibm.com",
}

# Deterministic red-flag domain TLDs / patterns
_SUSPICIOUS_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\.(xyz|tk|ml|ga|cf|gq|pw|cc)$", re.I),
    re.compile(r"(career|jobs|internship|placement|recruit)[s\-_]?(fast|quick|easy|instant|direct)", re.I),
    re.compile(r"(amazon|google|microsoft|wipro|infosys|tcs)[s\-_.]+(career|job|intern|hr)", re.I),
    re.compile(r"(onboard|join|verify)[s\-_.]+(now|today|pay|fee|deposit)", re.I),
]


class WebSearchAgent(InvestigationAgent):
    """Web verification agent using OpenCode runtime for live domain search.

    Performs:
    1. Entity extraction (companies, domains, emails, Telegram handles)
    2. Deterministic suspicious-domain analysis (instant, no LLM needed)
    3. OpenCode web search to verify company legitimacy (async subprocess)
    4. Trust signal generation — can reduce OR increase threat score
    """

    name = "web_search"
    _OPENCODE_TIMEOUT = 90  # seconds max per search round

    async def run(
        self, request: InvestigationRequest, context: AgentContext
    ) -> WebSearchResult | None:
        _console_log("Starting domain verification and web intelligence...")
        await context.log(request, self.name, "Web verification started")

        entities = self._extract_entities(request.raw_input)
        _console_log(f"Extracted entities: {entities}")

        # 1. Fast deterministic checks (no network needed)
        det_signals = self._deterministic_checks(entities)
        _console_log(f"Deterministic signals: {len(det_signals)}")

        # 2. OpenCode web search for live verification
        web_findings: dict[str, Any] = {}
        try:
            web_findings = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    self._run_opencode_search,
                    entities,
                    request.raw_input[:2000],
                ),
                timeout=self._OPENCODE_TIMEOUT,
            )
        except asyncio.TimeoutError:
            _console_log(f"OpenCode search timed out after {self._OPENCODE_TIMEOUT}s")
        except Exception as exc:
            _console_log(f"OpenCode search error: {exc}")

        # 3. Merge deterministic + web findings into trust signals
        trust_signals = det_signals + web_findings.get("trust_signals", [])
        suspicion_signals = web_findings.get("suspicion_signals", [])
        verified_entities = web_findings.get("verified_entities", [])
        unverified_entities = [e for e in entities.get("domains", []) if e not in verified_entities]

        # 4. Compute trust delta (negative = reduce score, positive = increase)
        trust_delta = self._compute_trust_delta(
            entities, trust_signals, suspicion_signals, verified_entities
        )

        result = WebSearchResult(
            investigation_id=request.investigation_id,
            extracted_entities=entities,
            trust_signals=trust_signals,
            suspicion_signals=suspicion_signals,
            verified_entities=verified_entities,
            unverified_entities=unverified_entities,
            trust_delta=trust_delta,
            web_summary=web_findings.get("summary", ""),
            search_performed=bool(web_findings),
        )

        _console_log(
            f"✓ Web verification complete | trust_delta={trust_delta:+d} | "
            f"verified={len(verified_entities)} | suspicion={len(suspicion_signals)}"
        )
        await context.log(
            request, self.name,
            f"Web check complete: trust_delta={trust_delta:+d}, verified={verified_entities}"
        )
        return result

    # ── OpenCode subprocess (v3.py pattern) ───────────────────────────────

    def _run_opencode_search(
        self, entities: dict[str, list[str]], raw_input_snippet: str
    ) -> dict[str, Any]:
        """Run OpenCode search in a subprocess using PTY (matches v3.py pattern)."""
        companies = entities.get("companies", [])
        domains = entities.get("domains", [])
        emails = entities.get("emails", [])

        search_targets = []
        for domain in domains[:3]:
            search_targets.append(f"site:{domain} careers OR jobs OR internship")
        for company in companies[:2]:
            search_targets.append(f'"{company}" official careers portal internship')
        for email in emails[:2]:
            domain = email.split("@")[-1] if "@" in email else ""
            if domain:
                search_targets.append(f"site:{domain} HR recruiter official")

        if not search_targets:
            _console_log("No search targets extracted — skipping OpenCode search")
            return {}

        prompt = f"""You are a cyber fraud investigator performing web verification.

RECRUITER MESSAGE EXCERPT:
---
{raw_input_snippet}
---

SEARCH TARGETS TO VERIFY:
{json.dumps(search_targets, indent=2)}

EXTRACTED ENTITIES:
- Companies: {companies}
- Domains: {domains}
- Emails: {emails}

TASKS:
1. Search the web for each target to verify legitimacy
2. Check if domains are official company-owned
3. Verify if careers/onboarding pages exist and look legitimate
4. Look for any fraud reports or scam warnings about these entities
5. Check if recruiter email domains match the claimed company

Return ONLY valid JSON:
{{
  "verified_entities": ["list of confirmed legitimate domains/entities"],
  "trust_signals": [
    {{"signal": "official_domain_verified", "entity": "...", "confidence": 0.9, "detail": "..."}}
  ],
  "suspicion_signals": [
    {{"signal": "domain_not_found", "entity": "...", "confidence": 0.8, "detail": "..."}}
  ],
  "summary": "2-3 sentence web verification summary"
}}"""

        cmd = ["opencode", "run", "-m", "opencode/big-pickle", "--dangerously-skip-permissions"]

        master_fd = None
        output_chunks: list[str] = []
        buffer = b""

        try:
            master_fd, slave_fd = pty.openpty()
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=slave_fd,
                stderr=slave_fd,
                text=False,
                close_fds=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
            os.close(slave_fd)
            process.stdin.write(prompt.encode("utf-8"))
            process.stdin.close()

            start = perf_counter()
            while True:
                ready, _, _ = select.select([master_fd], [], [], 0.25)
                if ready:
                    try:
                        chunk = os.read(master_fd, 4096)
                    except OSError:
                        chunk = b""
                    if chunk:
                        buffer += chunk
                        while b"\n" in buffer:
                            line, buffer = buffer.split(b"\n", 1)
                            decoded = line.decode("utf-8", errors="replace").rstrip("\r")
                            output_chunks.append(decoded)
                    elif process.poll() is not None:
                        break
                if process.poll() is not None and not ready:
                    break
                if perf_counter() - start > self._OPENCODE_TIMEOUT - 5:
                    process.kill()
                    break

            if buffer:
                decoded = buffer.decode("utf-8", errors="replace").rstrip("\r\n")
                if decoded:
                    output_chunks.append(decoded)

            process.wait(timeout=5)

        except Exception as exc:
            _console_log(f"Subprocess error: {exc}")
            return {}
        finally:
            if master_fd is not None:
                try:
                    os.close(master_fd)
                except OSError:
                    pass

        output_text = "\n".join(output_chunks)
        return self._extract_json_from_output(output_text)

    @staticmethod
    def _extract_json_from_output(text: str) -> dict[str, Any]:
        """Extract JSON from OpenCode output (handles markdown fencing)."""
        if not text:
            return {}
        # Markdown fenced blocks first
        for block in re.findall(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL):
            try:
                result = json.loads(block)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                continue
        # Raw JSON fallback
        brace_idx = text.find("{")
        if brace_idx != -1:
            for end in range(len(text), brace_idx, -1):
                try:
                    candidate = json.loads(text[brace_idx:end])
                    if isinstance(candidate, dict):
                        return candidate
                except json.JSONDecodeError:
                    continue
        return {}

    # ── Deterministic checks ──────────────────────────────────────────────

    def _deterministic_checks(self, entities: dict[str, list[str]]) -> list[dict[str, Any]]:
        """Fast rule-based domain checks — no LLM or network needed."""
        signals: list[dict[str, Any]] = []

        for domain in entities.get("domains", [])[:5]:
            # Check verified whitelist
            if domain.lower() in _VERIFIED_COMPANY_DOMAINS:
                signals.append({
                    "signal": "known_official_domain",
                    "entity": domain,
                    "confidence": 0.97,
                    "detail": f"{domain} is a verified official corporate domain",
                    "trust": True,
                })
                continue

            # Check suspicious patterns
            for pattern in _SUSPICIOUS_PATTERNS:
                if pattern.search(domain):
                    signals.append({
                        "signal": "suspicious_domain_pattern",
                        "entity": domain,
                        "confidence": 0.88,
                        "detail": f"Domain '{domain}' matches known fraud pattern",
                        "trust": False,
                    })
                    break

        for email in entities.get("emails", [])[:3]:
            if "@" in email:
                email_domain = email.split("@")[-1].lower()
                free_providers = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "yopmail.com"}
                if email_domain in free_providers:
                    signals.append({
                        "signal": "free_email_as_corporate_hr",
                        "entity": email,
                        "confidence": 0.82,
                        "detail": f"HR contact using free email provider: {email_domain}",
                        "trust": False,
                    })

        return signals

    # ── Entity extraction ─────────────────────────────────────────────────

    @staticmethod
    def _extract_entities(text: str) -> dict[str, list[str]]:
        """Extract companies, domains, emails, handles from recruiter message."""
        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-zA-Z]{2,}\b", text)
        domains_raw = re.findall(r"(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-z]{2,})", text)
        domains = [d for d in domains_raw if "." in d and len(d) > 4]
        handles = re.findall(r"@([a-zA-Z0-9_]{3,})", text)

        # Heuristic company name extraction (capitalized words near job-related nouns)
        company_candidates = re.findall(
            r"\b([A-Z][a-zA-Z&\s]{2,20}(?:Inc|Ltd|Corp|Technologies|Solutions|Pvt)?)\b"
            r"(?=\s+(?:internship|job|position|role|offer|recruitment|onboarding|hire))",
            text,
        )

        return {
            "emails": list(set(emails))[:5],
            "domains": list(set(domains))[:6],
            "handles": list(set(handles))[:4],
            "companies": list(set(c.strip() for c in company_candidates))[:3],
        }

    # ── Trust delta computation ───────────────────────────────────────────

    @staticmethod
    def _compute_trust_delta(
        entities: dict[str, list[str]],
        trust_signals: list[dict[str, Any]],
        suspicion_signals: list[dict[str, Any]],
        verified_entities: list[str],
    ) -> int:
        """Return score delta: negative = reduce threat score, positive = raise it."""
        delta = 0

        # Verified official domain → big trust reduction
        for sig in trust_signals:
            if sig.get("trust", False):
                if sig.get("signal") == "known_official_domain":
                    delta -= 30
                elif sig.get("signal") == "official_domain_verified":
                    delta -= 25
                else:
                    delta -= int(sig.get("confidence", 0.5) * 15)

        # Suspicion signals → raise score
        for sig in suspicion_signals:
            conf = sig.get("confidence", 0.5)
            if "not_found" in sig.get("signal", ""):
                delta += int(conf * 12)
            elif "scam" in sig.get("signal", "") or "fraud" in sig.get("signal", ""):
                delta += int(conf * 20)
            else:
                delta += int(conf * 8)

        # Free email as corporate → moderate raise
        for sig in trust_signals:
            if not sig.get("trust", True) and sig.get("signal") == "free_email_as_corporate_hr":
                delta += 10

        # Suspicious domain pattern → raise
        for sig in trust_signals:
            if not sig.get("trust", True) and sig.get("signal") == "suspicious_domain_pattern":
                delta += 15

        return max(-50, min(40, delta))
