"""AI-driven behavior analysis agent using NVIDIA Nemotron reasoning.

Analyzes recruiter communication patterns, urgency tactics, and social engineering
indicators to detect onboarding scams and impersonation attempts.

FORCES LIVE NVIDIA Nemotron Omni cognition for behavioral threat reasoning.
"""

import json
import logging
import sys
from time import perf_counter
from typing import Any

from app.agents.base import AgentContext, InvestigationAgent
from app.gateway.models import TextGenerationRequest
from app.gateway.text_router import TextRouter
from app.models.behavior_result import BehaviorResult, BehaviorSignal
from app.schemas.investigation import InvestigationRequest

logger = logging.getLogger(__name__)

def _console_log(message: str):
    """Direct console output for execution tracing."""
    print(f"[BEHAVIOR] {message}", file=sys.stderr, flush=True)


class BehaviorAnalysisAgent(InvestigationAgent):
    """AI-powered behavioral analysis agent.

    Uses NVIDIA Nemotron Omni reasoning model to:
    - Detect manipulation tactics
    - Identify urgency and coercion patterns
    - Recognize fake onboarding flows
    - Flag impersonation indicators
    - Generate structured reasoning output
    """

    name = "behavior_analysis"

    def __init__(self, text_router: TextRouter) -> None:
        self._text_router = text_router

    async def run(self, request: InvestigationRequest, context: AgentContext) -> BehaviorResult | None:
        """Execute AI-driven behavior analysis with NVIDIA Nemotron Omni cognition."""
        _console_log("Invoking NVIDIA Nemotron for behavioral threat analysis...")
        await context.log(request, self.name, "Starting AI behavioral analysis")

        system_prompt = """You are a CYBER THREAT INTELLIGENCE ANALYST specializing in recruitment fraud detection.

Your task is to analyze recruiter communications for SOCIAL ENGINEERING, FRAUD, and ONBOARDING SCAMS.

Apply deep cognitive analysis to detect:

1. URGENCY & PRESSURE TACTICS:
   - Artificial deadlines ("respond within 24 hours", "limited spots")
   - Escalation language ("urgent", "immediate action required")
   - Emotional manipulation ("lucky to be selected")

2. PAYMENT COERCION:
   - Refundable deposits ("refundable onboarding fee")
   - Advance payments ("processing fee", "training cost")
   - Payment extraction (UPI, wire transfer, cryptocurrency)
   - Multiple payment requests (suggests repeat extraction)

3. CHANNEL RESTRICTION:
   - Telegram-only communication (bypasses company infrastructure)
   - WhatsApp-only channels (unofficial routing)
   - Blocking official email (prevents audit trail)
   - Restricted communication ("don't mention to others")

4. IMPERSONATION TACTICS:
   - Domain spoofing (amazonjobs-careers.in vs amazon.com)
   - Brand impersonation (fake FAANG company emails)
   - Recruiter persona without company email

5. ONBOARDING FRAUD:
   - Fake offer letters
   - Forged documents
   - Incomplete hiring process
   - Missing standard HR procedures

6. BEHAVIORAL RED FLAGS:
   - Inconsistent communication
   - Pressure to bypass normal procedures
   - Reluctance to use official channels
   - Repetitive messaging patterns

Return ONLY valid JSON. No markdown. No code blocks."""

        user_prompt = f"""ANALYZE THIS RECRUITER COMMUNICATION FOR BEHAVIORAL THREATS:

---
{request.raw_input}
---

DEEP COGNITIVE REASONING REQUIRED:

1. Identify EVERY behavioral signal (urgency, payment, channel restriction, impersonation)
2. Assess CONFIDENCE for each signal (0.0-1.0 scale)
3. Determine OVERALL RISK SCORE (0-100)
4. Generate RECOMMENDED ACTION for SOC team

Return JSON with this exact structure:
{{
  "risk_score": <0-100>,
  "confidence": <0.0-1.0>,
  "signals": [
    {{
      "name": "<signal_identifier>",
	      "severity": "<low|medium|high|critical>",
	      "confidence": <0.0-1.0>,
	      "explanation": "<detailed_reasoning>",
	      "source": "ai_reasoned"
    }}
  ],
  "summary": "<2-3 sentence threat summary>",
  "recommended_action": "<action_description>",
  "reasoning_type": "behavioral_analysis"
}}

SIGNAL EXAMPLES: payment_extraction, non_official_channel, payment_coercion, urgency_pressure, telegram_impersonation, domain_spoofing, onboarding_fraud"""

        response_schema = {
            "type": "object",
            "properties": {
                "risk_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "signals": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
	                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
	                            "explanation": {"type": "string"},
	                            "source": {"type": "string"},
	                        },
	                        "required": ["name", "severity", "confidence", "explanation", "source"],
                    },
                },
                "summary": {"type": "string"},
                "recommended_action": {"type": "string"},
                "reasoning_type": {"type": "string"},
            },
            "required": ["risk_score", "confidence", "signals", "summary", "reasoning_type"],
        }

        try:
            _console_log("Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
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
                logger.error(f"Failed to parse AI response: {e}")
                # Attempt JSON recovery
                ai_output = self._recover_json(gen_response.content)
                if ai_output is None:
                    await context.log(request, self.name, "Failed to recover JSON from AI output")
                    return None

            # Extract and validate signals
            ai_signals = []
            if "signals" in ai_output and isinstance(ai_output["signals"], list):
                for sig in ai_output["signals"]:
                    try:
                        ai_signals.append(
                            BehaviorSignal(
                                name=sig.get("name", "unknown"),
                                severity=sig.get("severity", "medium"),
	                                confidence=min(1.0, max(0.0, float(sig.get("confidence", 0.5)))),
	                                explanation=sig.get("explanation", "")[:1000],
	                                source=sig.get("source", "ai_reasoned"),
	                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to parse signal: {e}")

            risk_score = min(100, max(0, int(ai_output.get("risk_score", 0))))
            confidence = min(1.0, max(0.0, float(ai_output.get("confidence", 0.5))))

            result = BehaviorResult(
                investigation_id=request.investigation_id,
                risk_score=risk_score,
                confidence=confidence,
                detected_patterns=[sig.name for sig in ai_signals],
                explanation=ai_output.get("summary", "")[:2000],
                provider=gen_response.provider,
                provider_model=gen_response.model,
                reasoning_type="behavioral_analysis",
                ai_signals=ai_signals,
                summary=ai_output.get("summary", "")[:500],
            )

            _console_log(f"✓ Behavioral cognition complete")
            _console_log(f"  Risk Score: {risk_score}/100")
            _console_log(f"  Confidence: {confidence:.0%}")
            _console_log(f"  Signals Detected: {len(ai_signals)}")
            _console_log(f"  Provider: {gen_response.provider.upper()}")
            for sig in ai_signals:
                _console_log(f"    • {sig.name}: {sig.severity.upper()} ({sig.confidence:.0%} confidence)")
            
            await context.log(
                request, self.name, f"Behavior analysis complete: risk_score={risk_score}, signals={len(ai_signals)}, provider={gen_response.provider}"
            )
            return result

        except Exception as e:
            logger.error(f"Behavior analysis failed: {e}", exc_info=True)
            await context.log(request, self.name, f"Error during analysis: {str(e)}")
            return None

    @staticmethod
    def _recover_json(content: str) -> dict[str, Any] | None:
        """Attempt to recover JSON from malformed AI output."""
        # Remove markdown code blocks
        content = content.replace("```json", "").replace("```", "")
        content = content.strip()

        # Try to find JSON object
        start_idx = content.find("{")
        end_idx = content.rfind("}")
        if start_idx != -1 and end_idx != -1:
            try:
                return json.loads(content[start_idx : end_idx + 1])
            except json.JSONDecodeError:
                pass

        return None
