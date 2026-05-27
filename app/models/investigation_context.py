from datetime import UTC, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.contracts.agent_result import AgentResult


class InvestigationEntities(BaseModel):
    urls: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    emails: list[str] = Field(default_factory=list)
    telegram_handles: list[str] = Field(default_factory=list)
    upi_ids: list[str] = Field(default_factory=list)


class InvestigationContext(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    correlation_id: UUID
    raw_input: str = Field(min_length=1)
    evidence_kind: str
    entities: InvestigationEntities = Field(default_factory=InvestigationEntities)
    agent_results: list[AgentResult] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def with_result(self, result: AgentResult) -> "InvestigationContext":
        clone = self.model_copy(deep=True)
        clone.agent_results.append(result)
        clone.updated_at = datetime.now(UTC)
        return clone

    def with_entities(self, entities: InvestigationEntities) -> "InvestigationContext":
        clone = self.model_copy(deep=True)
        clone.entities = entities
        clone.updated_at = datetime.now(UTC)
        return clone

