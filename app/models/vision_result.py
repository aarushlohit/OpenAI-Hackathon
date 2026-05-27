from pydantic import BaseModel, Field


class VisionResult(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    detected_artifacts: list[str] = Field(default_factory=list)
    suspicious_elements: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    provider: str = Field(default="deterministic_vision_pipeline", min_length=1)

