from __future__ import annotations

import sys

from app.agents.base import AgentContext, InvestigationAgent
from app.models.vision_result import VisionArtifact, VisionResult
from app.providers.nvidia_reasoning_client import NVIDIA_MODEL, NvidiaReasoningClient
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationInputKind, InvestigationRequest
from app.security.model_output_validator import ModelOutputValidator
from app.services.ocr import SafeOCRService


def _console_log(message: str) -> None:
    print(f"[VISION] {message}", file=sys.stderr, flush=True)


_VISION_SYSTEM_PROMPT = """You are a document forensics and visual threat intelligence specialist.

Analyze the provided evidence for indicators of document forgery, phishing, and onboarding scams.

Focus on:
- Offer letter authenticity and formatting
- Company branding accuracy and imitations
- Payment instruction artifacts
- Phishing portal indicators
- Telegram communication screenshots
- Suspicious fonts and layouts
- Watermark and security features
- Contact information legitimacy
- Onboarding flow inconsistencies

Return compact valid JSON only. No markdown. No prose outside JSON."""


class VisionAnalysisAgent(InvestigationAgent):
    name = "vision"

    def __init__(
        self,
        ocr_service: SafeOCRService,
        prompt_registry: PromptRegistry,
        nvidia_client: NvidiaReasoningClient | None = None,
    ) -> None:
        self._ocr_service = ocr_service
        self._prompt_registry = prompt_registry
        self._nvidia_client = nvidia_client
        self._validator = ModelOutputValidator()

    async def run(self, request: InvestigationRequest, context: AgentContext) -> VisionResult:
        await context.log(request, self.name, "Starting vision analysis")

        image_reference = (
            request.raw_input
            if request.kind in {InvestigationInputKind.IMAGE_REFERENCE, InvestigationInputKind.DOCUMENT_REFERENCE}
            else ""
        )
        ocr = await self._ocr_service.extract(image_reference=image_reference, fallback_text=request.raw_input)

        if self._nvidia_client is None:
            raise RuntimeError("NVIDIA runtime unavailable. Investigation aborted.")

        _console_log("NVIDIA vision cognition started...")
        _console_log(f"Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")

        user_prompt = f"""Analyze this evidence for visual threats:

EXTRACTED OCR TEXT:
---
{ocr.extracted_text}
---

OCR ARTIFACTS DETECTED: {', '.join(ocr.artifacts) or 'none'}

Perform deep visual analysis including:
1. Forgery detection
2. Brand impersonation assessment
3. Payment/scam artifact identification
4. Overall threat assessment

Return this JSON with real values:
{{"risk_score":0-100,"risk_level":"LOW|MEDIUM|HIGH|CRITICAL","confidence":0.0-1.0,
"artifacts":[{{"type":"...","description":"...","confidence":0.0-1.0,
"severity":"LOW|MEDIUM|HIGH|CRITICAL","location":"full_document","source":"ai_reasoned"}}],
"suspicious_elements":["..."],"summary":"...","recommended_action":"...",
"reasoning_type":"vision_analysis"}}"""

        if image_reference:
            ai_output, latency_ms = await self._nvidia_client.analyze_image(
                system_prompt=_VISION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                image_url=image_reference,
                image_ocr_text=ocr.extracted_text,
                temperature=0.15,
                max_tokens=1200,
            )
        else:
            ai_output, latency_ms = await self._nvidia_client.analyze_text(
                system_prompt=_VISION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.15,
                max_tokens=1200,
            )
        _console_log(f"Response received ({latency_ms}ms)")

        validated = self._validator.validate_vision_output(ai_output)
        ai_artifacts = [
            VisionArtifact(
                artifact_type=artifact.get("type", "unknown"),
                description=artifact.get("description", "")[:1000],
                confidence=min(1.0, max(0.0, float(artifact.get("confidence", 0.5)))),
                severity=artifact.get("severity", "medium"),
                location=artifact.get("location", ""),
                source=artifact.get("source", "ai_reasoned"),
            )
            for artifact in validated.get("artifacts", [])
        ]
        confidence = min(1.0, max(0.0, float(validated.get("confidence", 0.5))))
        ocr_confidence = min(1.0, max(0.0, float(validated.get("ocr_confidence", confidence))))
        all_artifacts = sorted(set([a.artifact_type for a in ai_artifacts] + ocr.artifacts))
        all_suspicious = sorted(set(validated.get("suspicious_elements", [])))
        metadata = self._nvidia_client.last_metadata
        provider = metadata.provider if metadata else "nvidia_nim"
        model = metadata.model if metadata else NVIDIA_MODEL

        _console_log("Vision cognition complete")
        _console_log(f"Confidence: {confidence:.0%}")
        _console_log(f"Artifacts Detected: {len(ai_artifacts)}")

        return VisionResult(
            investigation_id=request.investigation_id,
            detected_artifacts=all_artifacts,
            suspicious_elements=all_suspicious,
            confidence=confidence,
            provider=provider,
            provider_model=model,
            reasoning_type="vision_analysis",
            ai_artifacts=ai_artifacts,
            ocr_text=ocr.extracted_text[:10000],
            ocr_confidence=ocr_confidence,
            summary=validated.get("summary", "")[:500],
        )
