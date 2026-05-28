"""AI-driven audio analysis agent with transcription and behavioral reasoning.

Analyzes recruiter phone calls and voice communications to detect coercion,
urgency tactics, and social engineering patterns.
"""

import logging

from app.agents.base import AgentContext, InvestigationAgent
from app.gateway.audio_router import AudioRouter
from app.models.audio_result import AudioBehaviorSignal, AudioResult
from app.providers.nvidia_reasoning_client import NVIDIA_MODEL, NvidiaReasoningClient, NvidiaReasoningError
from app.schemas.investigation import InvestigationRequest
from app.security.model_output_validator import ModelOutputValidationError, ModelOutputValidator

logger = logging.getLogger(__name__)


class AudioAnalysisAgent(InvestigationAgent):
    """AI-powered audio analysis agent with transcription and behavioral reasoning.

    Uses NVIDIA Nemotron Omni audio model to:
    - Transcribe audio with high confidence
    - Detect coercive tone and language
    - Identify urgency and pressure tactics
    - Recognize payment extraction language
    - Flag impersonation patterns
    - Analyze behavioral signals in speech
    - Generate structured audio reasoning output
    """

    name = "audio_analysis"

    def __init__(
        self,
        audio_router: AudioRouter | None = None,
        nvidia_client: NvidiaReasoningClient | None = None,
    ) -> None:
        self._audio_router = audio_router
        self._nvidia_client = nvidia_client
        self._validator = ModelOutputValidator()

    async def run(self, request: InvestigationRequest, context: AgentContext) -> AudioResult | None:
        """Execute AI-driven audio analysis."""
        await context.log(request, self.name, "Starting AI audio analysis")

        audio_reference = self._get_audio_reference(request)
        if not audio_reference:
            await context.log(request, self.name, "No audio evidence provided, skipping audio analysis")
            return None
        if self._nvidia_client is None:
            await context.log(request, self.name, "No NVIDIA client configured, skipping audio cognition")
            return None

        system_prompt = """You are a forensic voice analyst specializing in recruitment scam detection.

Analyze the provided audio for indicators of social engineering, coercion, and onboarding fraud.

Focus on:
- Urgency and pressure in tone
- Coercive language patterns
- Payment extraction tactics
- Impersonation attempts
- Fake job offer claims
- Onboarding pressure
- Emotional manipulation
- Threat or intimidation markers

Return ONLY valid JSON. No markdown. No code blocks."""

        user_prompt = f"""Analyze this audio evidence for voice-based threats:

Audio: {audio_reference}

Perform complete analysis including:
1. Full transcription with confidence scoring
2. Behavioral signal detection
3. Tone and urgency assessment
4. Pattern matching against known scams

Return JSON with this exact structure:
{{
  "risk_score": <0-100>,
  "confidence": <0.0-1.0>,
  "transcription": "<full_audio_transcript>",
  "transcription_confidence": <0.0-1.0>,
  "duration_seconds": <duration>,
  "signals": [
    {{
      "name": "<signal_identifier>",
      "severity": "<low|medium|high|critical>",
      "confidence": <0.0-1.0>,
      "explanation": "<why_detected>",
      "timestamp_start": <seconds>,
      "timestamp_end": <seconds>,
      "source": "ai_reasoned"
    }}
  ],
  "detected_patterns": ["pattern1", "pattern2"],
  "recommended_action": "<action_description>",
  "summary": "<brief_audio_threat_summary>",
  "reasoning_type": "audio_analysis"
}}"""

        try:
            ai_output, latency_ms = await self._nvidia_client.analyze_audio(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                audio_url=audio_reference,
                audio_transcription_text=request.raw_input,
                max_tokens=1200,
            )
            await context.log(request, self.name, f"NVIDIA audio response received in {latency_ms}ms")
            ai_output = self._validator.validate_audio_output(ai_output)

            # Extract and validate signals
            ai_signals = []
            if "signals" in ai_output and isinstance(ai_output["signals"], list):
                for sig in ai_output["signals"]:
                    try:
                        ai_signals.append(
                            AudioBehaviorSignal(
                                name=sig.get("name", "unknown"),
                                severity=sig.get("severity", "medium"),
                                confidence=min(1.0, max(0.0, float(sig.get("confidence", 0.5)))),
                                explanation=sig.get("explanation", "")[:1000],
                                timestamp_start=max(0.0, float(sig.get("timestamp_start", 0.0))),
                                timestamp_end=max(0.0, float(sig.get("timestamp_end", 0.0))),
                                source=sig.get("source", "ai_reasoned"),
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to parse audio signal: {e}")

            risk_score = min(100, max(0, int(ai_output.get("risk_score", 0))))
            confidence = min(1.0, max(0.0, float(ai_output.get("confidence", 0.5))))
            transcription_confidence = min(1.0, max(0.0, float(ai_output.get("transcription_confidence", 0.5))))
            duration_seconds = max(0.0, float(ai_output.get("duration_seconds", 0.0)))

            result = AudioResult(
                investigation_id=request.investigation_id,
                risk_score=risk_score,
                confidence=confidence,
                provider="nvidia_nim",
                provider_model=NVIDIA_MODEL,
                reasoning_type="audio_analysis",
                transcription=ai_output.get("transcription", "")[:50000],
                transcription_confidence=transcription_confidence,
                ai_signals=ai_signals,
                detected_patterns=ai_output.get("detected_patterns", []),
                summary=ai_output.get("summary", "")[:500],
                duration_seconds=duration_seconds,
            )

            await context.log(request, self.name, f"Audio analysis complete: risk_score={risk_score}")
            return result

        except (NvidiaReasoningError, ModelOutputValidationError) as e:
            logger.error(f"Audio analysis failed: {e}", exc_info=True)
            await context.log(request, self.name, f"Error during analysis: {str(e)}")
            return None

    @staticmethod
    def _get_audio_reference(request: InvestigationRequest) -> str | None:
        if request.kind.value == "audio_reference":
            return request.raw_input
        return None
