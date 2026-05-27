from difflib import SequenceMatcher


class EntitySimilarity:
    def exact(self, left: str, right: str) -> bool:
        return left.strip().lower() == right.strip().lower()

    def fuzzy_score(self, left: str, right: str) -> float:
        return SequenceMatcher(None, left.lower(), right.lower()).ratio()

    def matches(self, left: str, right: str, threshold: float = 0.86) -> bool:
        return self.exact(left, right) or self.fuzzy_score(left, right) >= threshold

