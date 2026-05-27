from enum import StrEnum

from pydantic import BaseModel, Field


class ThreatSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatScore(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    final_score: int = Field(ge=0, le=100)
    severity: ThreatSeverity
    explanation: str = Field(min_length=1, max_length=2_000)
    contributing_factors: list[str] = Field(default_factory=list)

