from pydantic import BaseModel, Field


class AudioBehaviorSignal(BaseModel):
    """Behavioral signal detected from audio analysis."""

    name: str = Field(description="Signal identifier, e.g., 'coercive_tone', 'urgency_pressure'")
    severity: str = Field(description="Signal severity: low|medium|high|critical")
    confidence: float = Field(ge=0, le=1, description="Detection confidence 0-1")
    explanation: str = Field(max_length=1_000, description="Why this signal was detected")
    timestamp_start: float = Field(ge=0, description="Start time in seconds")
    timestamp_end: float = Field(ge=0, description="End time in seconds")
    source: str = Field(default="ai_reasoned", description="ai_reasoned|deterministic|hybrid|heuristic_fallback")


class AudioResult(BaseModel):
    """Audio investigation result with transcription and behavioral analysis."""

    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    provider: str = Field(min_length=1, description="Audio provider (transcription + reasoning)")
    provider_model: str = Field(min_length=1, description="Specific audio model version")
    reasoning_type: str = Field(default="audio_analysis", description="Type of audio reasoning applied")
    transcription: str = Field(max_length=50_000, description="Full audio transcription")
    transcription_confidence: float = Field(ge=0, le=1, description="Transcription confidence")
    ai_signals: list[AudioBehaviorSignal] = Field(
        default_factory=list, description="Behavioral signals extracted from audio"
    )
    detected_patterns: list[str] = Field(
        default_factory=list, description="Known scam/coercion patterns detected in speech"
    )
    summary: str = Field(default="", max_length=500, description="AI-generated audio analysis summary")
    duration_seconds: float = Field(ge=0, description="Total audio duration in seconds")
