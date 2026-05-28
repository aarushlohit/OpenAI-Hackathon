"""AI-driven vision analysis agent with OCR and multimodal reasoning.

Analyzes offer letters, screenshots, and visual evidence to detect document
forgery, fake branding, and phishing artifacts.
"""

import json
import logging
from typing import Any

from app.agents.base import AgentContext, InvestigationAgent
from app.gateway.models import VisionAnalysisRequest
from app.gateway.vision_router import VisionRouter
from app.models.vision_result import VisionArtifact, VisionResult
from app.schemas.investigation import InvestigationRequest

logger = logging.getLogger(__name__)


class VisionAnalysisAgent(InvestigationAgent):
    """AI-powered vision analysis agent with multimodal support.

    Uses NVIDIA Nemotron Omni vision model to:
    - Extract text via OCR and AI understanding
    - Detect fake offer letters
    - Identify forged company branding
    - Flag payment instructions
    - Recognize phishing portals
    - Detect Telegram onboarding artifacts
    - Analyze screenshots for scam indicators
    - Generate structured vision reasoning output
    """

    name = "vision_analysis"

    def __init__(self, vision_router: VisionRouter) -> None:
        self._vision_router = vision_router

    async def run(self, request: InvestigationRequest, context: AgentContext) -> VisionResult | None:
        """Execute AI-driven vision analysis."""
        await context.log(request, self.name, "Starting AI vision analysis")

        # Check if investigation has attached images
        if not request.evidence or not any(e.mime_type and "image" in e.mime_type for e in request.evidence):
            await context.log(request, self.name, "No image evidence provided, skipping vision analysis")
            return None

        system_prompt = """You are a document forensics and visual threat intelligence specialist.

Analyze the provided image for indicators of document forgery, phishing, and onboarding scams.

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

Return ONLY valid JSON. No markdown. No code blocks."""

        image_reference = self._get_image_reference(request)
        if not image_reference:
            await context.log(request, self.name, "Could not extract image reference")
            return None

        user_prompt = f"""Analyze this image evidence for visual threats:

Image: {image_reference}

Perform deep visual analysis including:
1. OCR text extraction
2. Forgery detection
3. Brand impersonation assessment
4. Payment/scam artifact identification
5. Overall threat assessment

Return JSON with this exact structure:
{{
  "risk_score": <0-100>,
  "confidence": <0.0-1.0>,
  "ocr_text": "<extracted_text>",
  "ocr_confidence": <0.0-1.0>,
  "artifacts": [
    {{
      "type": "<payment_instruction|forged_branding|phishing_portal|telegram_screenshot|onboarding_artifact|other>",
      "description": "<what_was_detected>",
      "confidence": <0.0-1.0>,
      "severity": "<low|medium|high|critical>",
      "location": "<top_left|top_right|center|bottom_left|bottom_right|full_document>"
    }}
  ],
  "suspicious_elements": ["element1", "element2"],
  "summary": "<brief_visual_threat_summary>",
  "reasoning_type": "vision_analysis"
}}"""

        response_schema = {
            "type": "object",
            "properties": {
                "risk_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "ocr_text": {"type": "string"},
                "ocr_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "artifacts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "description": {"type": "string"},
                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                            "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                            "location": {"type": "string"},
                        },
                        "required": ["type", "description", "confidence"],
                    },
                },
                "suspicious_elements": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"},
                "reasoning_type": {"type": "string"},
            },
            "required": ["risk_score", "confidence", "artifacts", "summary", "reasoning_type"],
        }

        try:
            vision_response = await self._vision_router.analyze(
                request=VisionAnalysisRequest(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    image_reference=image_reference,
                    response_schema=response_schema,
                ),
                investigation_id=request.investigation_id,
                correlation_id=request.correlation_id,
            )

            await context.log(request, self.name, f"AI vision model returned response from {vision_response.provider}")

            # Parse and validate vision response
            try:
                ai_output: dict[str, Any] = json.loads(vision_response.content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse vision response: {e}")
                return None

            # Extract and validate artifacts
            ai_artifacts = []
            if "artifacts" in ai_output and isinstance(ai_output["artifacts"], list):
                for artifact in ai_output["artifacts"]:
                    try:
                        ai_artifacts.append(
                            VisionArtifact(
                                artifact_type=artifact.get("type", "unknown"),
                                description=artifact.get("description", "")[:1000],
                                confidence=min(1.0, max(0.0, float(artifact.get("confidence", 0.5)))),
                                severity=artifact.get("severity", "medium"),
                                location=artifact.get("location", ""),
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to parse artifact: {e}")

            risk_score = min(100, max(0, int(ai_output.get("risk_score", 0))))
            confidence = min(1.0, max(0.0, float(ai_output.get("confidence", 0.5))))
            ocr_confidence = min(1.0, max(0.0, float(ai_output.get("ocr_confidence", 0.5))))

            result = VisionResult(
                investigation_id=request.investigation_id,
                detected_artifacts=[a.artifact_type for a in ai_artifacts],
                suspicious_elements=ai_output.get("suspicious_elements", []),
                confidence=confidence,
                provider=vision_response.provider,
                provider_model=vision_response.model,
                reasoning_type="vision_analysis",
                ai_artifacts=ai_artifacts,
                ocr_text=ai_output.get("ocr_text", "")[:10000],
                ocr_confidence=ocr_confidence,
                summary=ai_output.get("summary", "")[:500],
                metadata={
                    "analysis_timestamp": str(__import__("datetime").datetime.utcnow().isoformat()),
                    "image_count": str(len([e for e in request.evidence if e.mime_type and "image" in e.mime_type])),
                },
            )

            await context.log(request, self.name, f"Vision analysis complete: risk_score={risk_score}")
            return result

        except Exception as e:
            logger.error(f"Vision analysis failed: {e}", exc_info=True)
            await context.log(request, self.name, f"Error during analysis: {str(e)}")
            return None

    @staticmethod
    def _get_image_reference(request: InvestigationRequest) -> str | None:
        """Extract image reference from evidence."""
        if not request.evidence:
            return None

        for evidence in request.evidence:
            if evidence.mime_type and "image" in evidence.mime_type:
                # In real environment, this would be a URL or file reference
                # For now, return a reference ID
                return f"image://{evidence.artifact_id}"

        return None
