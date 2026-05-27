from pydantic import BaseModel, Field


class BehaviorResult(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    detected_patterns: list[str] = Field(default_factory=list)
    explanation: str = Field(min_length=1, max_length=2_000)
    provider: str = Field(default="deterministic_behavior_engine", min_length=1)
    provider_model: str = Field(default="ruleset-v1", min_length=1)

