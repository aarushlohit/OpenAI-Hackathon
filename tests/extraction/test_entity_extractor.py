import unittest

from app.extraction import EntityExtractor


class EntityExtractorTests(unittest.TestCase):
    def test_extracts_urls_domains_telegram_and_upi(self) -> None:
        entities = EntityExtractor().extract(
            "Apply at https://new-careers.xyz/verify contact @fakehr and pay internpay@upi"
        )

        self.assertIn("https://new-careers.xyz/verify", entities.urls)
        self.assertIn("new-careers.xyz", entities.domains)
        self.assertIn("fakehr", entities.telegram_handles)
        self.assertIn("internpay@upi", entities.upi_ids)

