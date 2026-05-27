from app.agents.base import AgentContext, InvestigationAgent
from app.models.vision_result import VisionResult
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationInputKind, InvestigationRequest
from app.services.ocr import SafeOCRService


class VisionAnalysisAgent(InvestigationAgent):
    name = "vision"

    suspicious_terms = {
        "deposit": "onboarding_payment_screenshot",
        "payment": "payment_instruction",
        "offer letter": "offer_letter_anomaly",
        "telegram": "telegram_onboarding_artifact",
        "login": "portal_login_capture",
        "verify account": "credential_verification_prompt",
    }

    def __init__(self, ocr_service: SafeOCRService, prompt_registry: PromptRegistry) -> None:
        self._ocr_service = ocr_service
        self._prompt_registry = prompt_registry

    async def run(self, request: InvestigationRequest, context: AgentContext) -> VisionResult:
        await context.log(request, self.name, "Running OCR before multimodal artifact analysis")
        self._prompt_registry.load("vision", "system_prompt")
        image_reference = request.raw_input if request.kind == InvestigationInputKind.IMAGE_REFERENCE else ""
        ocr = await self._ocr_service.extract(image_reference=image_reference, fallback_text=request.raw_input)
        lowered = ocr.extracted_text.lower()
        suspicious = [label for term, label in self.suspicious_terms.items() if term in lowered]
        confidence = min(0.9, 0.3 + (len(suspicious) * 0.14) + (len(ocr.artifacts) * 0.08))
        await context.log(request, self.name, f"OCR produced {len(ocr.artifacts)} artifact hint(s)")
        return VisionResult(
            investigation_id=request.investigation_id,
            detected_artifacts=ocr.artifacts,
            suspicious_elements=sorted(set(suspicious)),
            confidence=confidence,
        )

