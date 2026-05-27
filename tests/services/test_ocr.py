import unittest

from app.services.ocr import SafeOCRService


class OCRTests(unittest.IsolatedAsyncioTestCase):
    async def test_sanitizes_control_characters(self) -> None:
        result = await SafeOCRService().extract("image.png", "Offer letter\x00 requires deposit")

        self.assertNotIn("\x00", result.extracted_text)
        self.assertIn("offer_letter_text", result.artifacts)
        self.assertIn("payment_instruction_text", result.artifacts)

