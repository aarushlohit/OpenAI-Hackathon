import unittest

from app.api.protection_models import build_lookup


class ProtectionLookupTests(unittest.TestCase):
    def test_related_entities_are_elevated(self) -> None:
        result = build_lookup("fake.example", "domain", ["INV-ABCDEF12"])

        self.assertEqual(result.risk, "elevated")
