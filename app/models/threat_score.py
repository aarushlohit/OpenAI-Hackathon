from enum import StrEnum

from pydantic import BaseModel, Field


class ThreatSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EvidenceSignal(BaseModel):
    """A single weighted evidence signal contributing to the threat score."""

    signal: str = Field(description="Signal identifier, e.g. 'urgency_manipulation'")
    weight: float = Field(ge=0.0, le=1.0, description="Normalised contribution weight 0-1")
    score_contribution: int = Field(ge=0, le=100, description="Raw points added to final score")
    confidence: float = Field(ge=0.0, le=1.0, description="Evidence confidence 0-1")
    source: str = Field(default="agent", description="Originating agent or module (ai:*, deterministic_*, consensus_*)")
    detail: str = Field(default="", description="Human-readable evidence detail")


class ThreatScore(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    final_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0, description="Aggregate investigation confidence")
    severity: ThreatSeverity
    explanation: str = Field(min_length=1, max_length=2_000)
    explainability_summary: str = Field(
        default="",
        max_length=4_000,
        description="Structured NL explanation of why the verdict was reached",
    )
    contributing_factors: list[str] = Field(default_factory=list)
    evidence_breakdown: list[EvidenceSignal] = Field(
        default_factory=list,
        description="Per-signal evidence decomposition for explainability panel",
    )
    verdict_source: str = Field(
        default="hybrid_correlation",
        description="Verdict source: ai_reasoning|deterministic_validation|hybrid_correlation",
    )
    primary_cognition: str = Field(default="nvidia_nim", description="Primary AI model used: nvidia_nim|openai|fallback")
    deterministic_validation: bool = Field(
        default=True, description="Whether deterministic validation confirmed findings"
    )
    cross_agent_consensus: bool = Field(default=False, description="Whether multiple agents reached consensus")

