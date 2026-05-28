from pydantic import BaseModel, Field


class BehaviorSignal(BaseModel):
    """Single behavioral threat signal with reasoning."""

    name: str = Field(description="Signal identifier, e.g., 'payment_coercion'")
    severity: str = Field(description="Signal severity: low|medium|high|critical")
    confidence: float = Field(ge=0, le=1, description="Signal confidence 0-1")
    explanation: str = Field(max_length=1_000, description="Why this signal was detected")
    source: str = Field(default="ai_reasoned", description="ai_reasoned|deterministic|hybrid|heuristic_fallback")


class BehaviorResult(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    detected_patterns: list[str] = Field(default_factory=list)
    explanation: str = Field(min_length=1, max_length=2_000)
    provider: str = Field(min_length=1, description="AI provider used for reasoning")
    provider_model: str = Field(min_length=1, description="Specific model version")
    reasoning_type: str = Field(default="behavioral_analysis", description="Type of AI reasoning applied")
    ai_signals: list[BehaviorSignal] = Field(
        default_factory=list, description="Structured signals from AI reasoning"
    )
    summary: str = Field(default="", max_length=500, description="AI-generated summary of findings")
