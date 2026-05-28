import re
from pathlib import Path

from pydantic import BaseModel, Field


class OCRResult(BaseModel):
    extracted_text: str = Field(max_length=20_000)
    artifacts: list[str] = Field(default_factory=list)


class SafeOCRService:
    control_chars = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

    async def extract(self, image_reference: str, fallback_text: str = "") -> OCRResult:
        if image_reference:
            path = Path(image_reference)
            if path.exists() and path.suffix.lower() == ".pdf":
                text = self._extract_pdf(path)
                return OCRResult(extracted_text=text, artifacts=self._artifact_hints(text))
            if path.exists():
                text = self._extract_image(path)
                return OCRResult(extracted_text=text, artifacts=self._artifact_hints(text))
            if fallback_text:
                sanitized = self.control_chars.sub("", fallback_text)
                return OCRResult(extracted_text=sanitized.strip(), artifacts=self._artifact_hints(sanitized))
            raise RuntimeError(f"OCR artifact does not exist: {image_reference}")

        sanitized = self.control_chars.sub("", fallback_text)
        if not sanitized.strip():
            raise RuntimeError("OCR requires an image/PDF path or explicit extracted text")
        return OCRResult(extracted_text=sanitized.strip(), artifacts=self._artifact_hints(sanitized))

    def _extract_image(self, path: Path) -> str:
        try:
            from PIL import Image
            import pytesseract
        except ImportError as exc:
            raise RuntimeError("Real OCR requires Pillow and pytesseract") from exc

        try:
            text = pytesseract.image_to_string(Image.open(path))
        except Exception as exc:
            raise RuntimeError(f"OCR failed for {path}: {exc}") from exc
        sanitized = self.control_chars.sub("", text).strip()
        if not sanitized:
            raise RuntimeError(f"OCR produced no text for {path}")
        return sanitized[:20_000]

    def _extract_pdf(self, path: Path) -> str:
        errors: list[str] = []
        for module_name in ("pypdf", "PyPDF2"):
            try:
                module = __import__(module_name, fromlist=["PdfReader"])
                reader = module.PdfReader(str(path))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                sanitized = self.control_chars.sub("", text).strip()
                if sanitized:
                    return sanitized[:20_000]
                errors.append(f"{module_name} produced no text")
            except ImportError as exc:
                errors.append(f"{module_name} unavailable: {exc}")
            except Exception as exc:
                errors.append(f"{module_name} failed: {exc}")
        raise RuntimeError("; ".join(errors) or f"PDF extraction failed for {path}")

    def _artifact_hints(self, text: str) -> list[str]:
        artifacts: list[str] = []
        lowered = text.lower()
        if "offer letter" in lowered:
            artifacts.append("offer_letter_text")
        if "payment" in lowered or "deposit" in lowered or "upi" in lowered:
            artifacts.append("payment_instruction_text")
        if "telegram" in lowered:
            artifacts.append("telegram_text")
        if "login" in lowered or "portal" in lowered:
            artifacts.append("portal_text")
        return artifacts
