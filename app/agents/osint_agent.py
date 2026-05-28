"""AI-driven OSINT agent using NVIDIA Nemotron reasoning.

Analyzes domain information, reputation indicators, and phishing patterns
to detect suspicious recruitment infrastructure.

FORCES LIVE NVIDIA Nemotron Omni cognition for infrastructure threat reasoning.
"""

import json
import logging
import sys
from time import perf_counter
from typing import Any

from app.agents.base import AgentContext, InvestigationAgent
from app.gateway.models import TextGenerationRequest
from app.gateway.text_router import TextRouter
from app.models.osint_result import OSINTIndicator, OSINTResult
from app.schemas.investigation import InvestigationRequest

logger = logging.getLogger(__name__)

def _console_log(message: str):
    """Direct console output for execution tracing."""
    print(f"[OSINT] {message}", file=sys.stderr, flush=True)


class OSINTAgent(InvestigationAgent):
    """AI-powered OSINT analysis agent.

    Uses NVIDIA Nemotron Omni reasoning model to:
    - Interpret domain age and registration patterns
    - Analyze WHOIS anomalies
    - Evaluate reputation indicators
    - Detect phishing similarities
    - Identify fake HR infrastructure patterns
    - Generate structured intelligence output
    """

    name = "osint"

    def __init__(self, text_router: TextRouter) -> None:
        self._text_router = text_router

    async def run(self, request: InvestigationRequest, context: AgentContext) -> OSINTResult | None:
        """Execute AI-driven OSINT analysis with NVIDIA Nemotron Omni cognition."""
        _console_log("Invoking NVIDIA Nemotron for infrastructure threat analysis...")
        await context.log(request, self.name, "Starting AI OSINT analysis")

        system_prompt = """You are a CYBERSECURITY ANALYST specializing in threat intelligence and phishing detection.

Your task is to analyze recruitment communications for indicators of MALICIOUS INFRASTRUCTURE, DOMAIN ANOMALIES,
and PHISHING PATTERNS.

Apply deep cognitive analysis to detect:

1. DOMAIN REGISTRATION ANOMALIES:
   - Newly registered domains (< 30 days old)
   - Typosquatting (amazonjobs-careers.in vs amazon.com)
   - Dynamic DNS (suggests fast evasion)
   - Bulletproof hosting providers

2. TLS/SSL SUSPICIOUS PATTERNS:
   - Self-signed certificates
   - Expired SSL
   - Mismatched certificate domain
   - Uncommon certificate authorities

3. PHISHING INFRASTRUCTURE:
   - Known phishing hosting providers
   - Compromised legitimate domains
   - URL shorteners (masking destination)
   - Suspicious redirects

4. RECRUITER INFRASTRUCTURE:
   - Free email domains (@gmail.com, @hotmail.com for company HR)
   - Disposable email providers
   - Telegram-only recruitment (no official domain)
   - Unusual communication channels

5. PAYMENT INFRASTRUCTURE:
   - UPI payment requests (informal channels)
   - Unknown payment processors
   - Cryptocurrency payment (irreversible)
   - Multiple payment routing

6. REPUTATION & BLACKLIST SIGNALS:
   - Domain on fraud blacklists
   - Known recruiter scam campaigns
   - Phishing site database hits
   - Previous scam infrastructure

Return ONLY valid JSON. No markdown. No code blocks."""

        # Extract domains/emails from input for targeted analysis
        targets = self._extract_targets(request.raw_input)
        targets_str = ", ".join(targets[:5]) if targets else "N/A"

        user_prompt = f"""ANALYZE THIS RECRUITER COMMUNICATION FOR INFRASTRUCTURE THREATS:

---
{request.raw_input}
---

DEEP COGNITIVE REASONING REQUIRED:

1. Extract all domains, emails, payment handles, Telegram accounts
2. Assess domain age, registration anomalies, certificate issues
3. Evaluate infrastructure reputation and blacklist indicators
4. Determine OVERALL REPUTATION SCORE (0-100, where 0 is most suspicious)
5. Generate RECOMMENDED ACTION for threat investigation team

EXTRACTED TARGETS FOR ANALYSIS: {targets_str}

Return JSON with this exact structure:
{{
  "domain_age_days": <integer_or_null>,
  "ssl_valid": <true|false|null>,
  "reputation_score": <0-100>,
  "confidence": <0.0-1.0>,
  "indicators": [
    {{
      "name": "<indicator_identifier>",
      "severity": "<low|medium|high|critical>",
      "confidence": <0.0-1.0>,
      "evidence": "<detailed_reasoning>"
    }}
  ],
  "summary": "<2-3 sentence infrastructure assessment>"
}}

INDICATOR EXAMPLES: newly_registered_domain, typosquatting, phishing_infrastructure, free_email_domain, telegram_impersonation, ssl_invalid, payment_infrastructure_suspicious"""

        response_schema = {
            "type": "object",
            "properties": {
                "domain_age_days": {"type": ["integer", "null"], "minimum": 0},
                "ssl_valid": {"type": ["boolean", "null"]},
                "reputation_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "suspicious_indicators": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "indicators": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "evidence": {"type": "string"},
                        },
                        "required": ["name", "severity", "confidence", "evidence"],
                    },
                },
                "summary": {"type": "string"},
            },
            "required": ["reputation_score", "confidence", "indicators", "summary"],
        }

        try:
            _console_log(f"Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
            _console_log(f"Infrastructure targets: {targets_str}")
            start_time = perf_counter()
            
            gen_response = await self._text_router.generate(
                request=TextGenerationRequest(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_schema=response_schema,
                    temperature=0.1,
                ),
                investigation_id=request.investigation_id,
                correlation_id=request.correlation_id,
            )

            latency_ms = int((perf_counter() - start_time) * 1000)
            _console_log(f"Response latency: {latency_ms}ms from {gen_response.provider.upper()}")
            
            await context.log(request, self.name, f"AI cognition complete: {gen_response.provider} ({latency_ms}ms)")

            # Parse and validate AI response
            try:
                ai_output: dict[str, Any] = json.loads(gen_response.content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI OSINT response: {e}")
                return None

            # Extract and validate indicators
            ai_indicators = []
            if "indicators" in ai_output and isinstance(ai_output["indicators"], list):
                for ind in ai_output["indicators"]:
                    try:
                        ai_indicators.append(
                            OSINTIndicator(
                                name=ind.get("name", "unknown"),
                                severity=ind.get("severity", "medium"),
                                confidence=min(1.0, max(0.0, float(ind.get("confidence", 0.5)))),
                                evidence=ind.get("evidence", "")[:1000],
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to parse OSINT indicator: {e}")

            reputation_score = min(100, max(0, int(ai_output.get("reputation_score", 50))))
            confidence = min(1.0, max(0.0, float(ai_output.get("confidence", 0.5))))

            result = OSINTResult(
                investigation_id=request.investigation_id,
                domain_age_days=ai_output.get("domain_age_days"),
                ssl_valid=ai_output.get("ssl_valid"),
                reputation_score=reputation_score,
                suspicious_indicators=ai_output.get("suspicious_indicators", []),
                confidence=confidence,
                provider=gen_response.provider,
                provider_model=gen_response.model,
                reasoning_type="osint_analysis",
                ai_indicators=ai_indicators,
                summary=ai_output.get("summary", "")[:500],
            )

            _console_log(f"✓ Infrastructure cognition complete")
            _console_log(f"  Reputation Score: {reputation_score}/100")
            _console_log(f"  Confidence: {confidence:.0%}")
            _console_log(f"  Indicators Detected: {len(ai_indicators)}")
            _console_log(f"  Provider: {gen_response.provider.upper()}")
            for ind in ai_indicators:
                _console_log(f"    • {ind.name}: {ind.severity.upper()} ({ind.confidence:.0%} confidence)")
            
            await context.log(request, self.name, f"OSINT analysis complete: reputation={reputation_score}, indicators={len(ai_indicators)}, provider={gen_response.provider}")
            return result

        except Exception as e:
            logger.error(f"OSINT analysis failed: {e}", exc_info=True)
            await context.log(request, self.name, f"Error during analysis: {str(e)}")
            return None

    @staticmethod
    def _extract_targets(text: str) -> list[str]:
        """Extract domains, emails, and handles from text."""
        import re

        targets = []
        # Extract emails
        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        targets.extend(emails[:3])

        # Extract domains
        domains = re.findall(r"(?:https?://)?(?:www\.)?([a-zA-Z0-9.-]+\.[a-z]{2,})", text)
        targets.extend(domains[:3])

        # Extract Telegram handles
        handles = re.findall(r"@([a-zA-Z0-9_]+)", text)
        targets.extend(handles[:3])

        return list(set(targets))
