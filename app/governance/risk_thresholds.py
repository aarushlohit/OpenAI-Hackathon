from pydantic import BaseModel, Field


class RiskThresholds(BaseModel):
    medium: int = Field(default=35, ge=0, le=100)
    high: int = Field(default=65, ge=0, le=100)
    critical: int = Field(default=85, ge=0, le=100)

