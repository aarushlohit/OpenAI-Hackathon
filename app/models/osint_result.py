from pydantic import BaseModel, Field


class OSINTResult(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    domain_age_days: int | None = Field(default=None, ge=0)
    ssl_valid: bool | None = None
    reputation_score: int = Field(ge=0, le=100)
    suspicious_indicators: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)

