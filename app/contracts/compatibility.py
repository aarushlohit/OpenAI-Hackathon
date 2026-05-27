from pydantic import BaseModel


class CompatibilityResult(BaseModel):
    compatible: bool
    reason: str


class CompatibilityChecker:
    def backward_compatible(self, old_fields: set[str], new_fields: set[str]) -> CompatibilityResult:
        missing = old_fields - new_fields
        if missing:
            return CompatibilityResult(compatible=False, reason=f"removed fields: {sorted(missing)}")
        return CompatibilityResult(compatible=True, reason="compatible")

