from pydantic import BaseModel, Field


class InvestigationLineage(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    parent_investigation_ids: list[str] = Field(default_factory=list)
    child_investigation_ids: list[str] = Field(default_factory=list)
    inherited_evidence: list[str] = Field(default_factory=list)
    campaign_id: str | None = None

