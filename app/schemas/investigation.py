from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from app.models.identifiers import new_investigation_id


class InvestigationInputKind(StrEnum):
    TEXT = "text"
    URL = "url"
    DOCUMENT_REFERENCE = "document_reference"
    IMAGE_REFERENCE = "image_reference"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InvestigationRequest(BaseModel):
    raw_input: str = Field(min_length=1, max_length=20_000)
    kind: InvestigationInputKind = InvestigationInputKind.TEXT
    source_url: HttpUrl | None = None
    investigation_id: str = Field(default_factory=new_investigation_id, pattern=r"^INV-[A-F0-9]{8}$")
    correlation_id: UUID = Field(default_factory=uuid4)
    received_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EvidenceItem(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    detail: str = Field(min_length=1, max_length=2_000)
    confidence: float = Field(ge=0, le=1)


class InvestigationFinding(BaseModel):
    summary: str = Field(min_length=1, max_length=500)
    risk_level: RiskLevel
    evidence: list[EvidenceItem] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list, max_length=10)


class InvestigationResult(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    correlation_id: UUID
    finding: InvestigationFinding
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
