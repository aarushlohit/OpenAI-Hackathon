import re

from pydantic import BaseModel, Field


class OCRResult(BaseModel):
    extracted_text: str = Field(max_length=20_000)
    artifacts: list[str] = Field(default_factory=list)


class SafeOCRService:
    control_chars = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

    async def extract(self, image_reference: str, fallback_text: str = "") -> OCRResult:
        sanitized = self.control_chars.sub("", fallback_text or image_reference)
        artifacts: list[str] = []
        lowered = sanitized.lower()
        if "offer letter" in lowered:
            artifacts.append("offer_letter_text")
        if "payment" in lowered or "deposit" in lowered:
            artifacts.append("payment_instruction_text")
        if "login" in lowered or "portal" in lowered:
            artifacts.append("portal_text")
        return OCRResult(extracted_text=sanitized.strip(), artifacts=artifacts)

