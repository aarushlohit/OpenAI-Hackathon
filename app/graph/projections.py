from enum import StrEnum

from pydantic import BaseModel, Field


class ThreatNodeKind(StrEnum):
    INVESTIGATION = "investigation"
    DOMAIN = "domain"
    EMAIL = "email"
    TELEGRAM = "telegram"
    UPI = "upi"
    PHONE = "phone"
    COMPANY_ALIAS = "company_alias"
    OFFER_SIGNATURE = "offer_signature"
    RECRUITER_NAME = "recruiter_name"
    PAYMENT_WALLET = "payment_wallet"


class ThreatEdgeKind(StrEnum):
    LINKED_TO = "linked_to"
    REUSED_BY = "reused_by"
    IMPERSONATES = "impersonates"
    SHARES_PAYMENT_METHOD = "shares_payment_method"
    SHARES_DOMAIN_PATTERN = "shares_domain_pattern"
    SHARES_TEMPLATE = "shares_template"
    SHARES_SIGNATURE = "shares_signature"


class ThreatGraphNode(BaseModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    kind: ThreatNodeKind
    severity: str = "unknown"


class ThreatGraphEdge(BaseModel):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    kind: ThreatEdgeKind
    confidence: float = Field(default=0.5, ge=0, le=1)


class ThreatGraphProjection(BaseModel):
    investigation_id: str = Field(pattern=r"^INV-[A-F0-9]{8}$")
    nodes: list[ThreatGraphNode] = Field(default_factory=list)
    edges: list[ThreatGraphEdge] = Field(default_factory=list)

