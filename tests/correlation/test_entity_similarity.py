import unittest

from app.intelligence import EntitySimilarity


class EntitySimilarityTests(unittest.TestCase):
    def test_fuzzy_alias_match(self) -> None:
        similarity = EntitySimilarity()

        self.assertTrue(similarity.matches("Acme Careers", "acme career"))

