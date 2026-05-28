from pydantic import BaseModel, Field


class VisionArtifact(BaseModel):
    """Detected artifact in visual evidence with AI interpretation."""

    artifact_type: str = Field(description="Type: payment_instruction|forged_branding|phishing_portal|telegram_screenshot|onboarding_artifact")
    description: str = Field(max_length=1_000, description="What was detected")
    confidence: float = Field(ge=0, le=1, description="Detection confidence 0-1")
    severity: str = Field(default="medium", description="Artifact severity: low|medium|high|critical")
    location: str = Field(default="", description="Location in image (e.g., 'top_right', 'center')")
    source: str = Field(default="ai_reasoned", description="ai_reasoned|deterministic|hybrid|heuristic_fallback")


class VisionResult(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    detected_artifacts: list[str] = Field(default_factory=list)
    suspicious_elements: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    provider: str = Field(min_length=1, default="deterministic_vision_pipeline", description="AI/deterministic provider")
    provider_model: str = Field(default="", description="Specific vision model version")
    reasoning_type: str = Field(default="vision_analysis", description="Analysis type: ocr|vision_ai|multimodal")
    ai_artifacts: list[VisionArtifact] = Field(
        default_factory=list, description="Structured artifacts from AI vision reasoning"
    )
    ocr_text: str = Field(default="", max_length=10_000, description="Extracted text from OCR")
    ocr_confidence: float = Field(default=0.0, ge=0, le=1, description="OCR extraction confidence")
    summary: str = Field(default="", max_length=500, description="Vision analysis summary")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Image metadata (format, dimensions, detection timestamp)"
    )
