from pydantic import BaseModel, Field


class OSINTIndicator(BaseModel):
    """Single OSINT threat indicator with AI interpretation."""

    name: str = Field(description="Indicator name, e.g., 'suspicious_domain_age'")
    severity: str = Field(description="Indicator severity: low|medium|high|critical")
    confidence: float = Field(ge=0, le=1, description="Indicator confidence 0-1")
    evidence: str = Field(max_length=1_000, description="Evidence supporting the indicator")
    source: str = Field(default="ai_reasoned", description="ai_reasoned|deterministic|hybrid|heuristic_fallback")


class OSINTResult(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    domain_age_days: int | None = Field(default=None, ge=0)
    ssl_valid: bool | None = None
    reputation_score: int = Field(ge=0, le=100)
    suspicious_indicators: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    provider: str = Field(default="", min_length=0, description="AI provider used for intelligence gathering")
    provider_model: str = Field(default="", min_length=0, description="Specific model version if AI-powered")
    reasoning_type: str = Field(
        default="osint_analysis", description="Type of analysis: deterministic|ai|hybrid"
    )
    ai_indicators: list[OSINTIndicator] = Field(
        default_factory=list, description="Structured indicators from AI reasoning"
    )
    summary: str = Field(default="", max_length=500, description="AI-generated OSINT summary")
