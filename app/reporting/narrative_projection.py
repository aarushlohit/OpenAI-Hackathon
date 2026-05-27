from pydantic import BaseModel, Field


class NarrativeProjection(BaseModel):
    investigation_id: str
    headline: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)

