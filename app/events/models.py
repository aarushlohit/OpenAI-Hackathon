from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from app.events.trace_context import TraceContext


class EventName(StrEnum):
    INVESTIGATION_STARTED = "investigation_started"
    INVESTIGATION_PROGRESS = "investigation_progress"
    INVESTIGATION_REQUESTED = "investigation_requested"
    AGENT_STARTED = "agent_started"
    AGENT_PROGRESS = "agent_progress"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    THREAT_DETECTED = "threat_detected"
    PROVIDER_FAILED = "provider_failed"
    PROVIDER_FALLBACK_USED = "provider_fallback_used"
    PROVIDER_FAILOVER = "provider_failover"
    INVESTIGATION_COMPLETED = "investigation_completed"
    INVESTIGATION_REPLAY = "investigation_replay"
    GRAPH_NODE_ADDED = "graph_node_added"
    GRAPH_EDGE_ADDED = "graph_edge_added"
    CAMPAIGN_DETECTED = "campaign_detected"
    ENTITY_CORRELATED = "entity_correlated"
    THREAT_FEED_UPDATE = "threat_feed_update"
    CAMPAIGN_EXPANDED = "campaign_expanded"
    AUTONOMOUS_ALERT = "autonomous_alert"
    RECURRING_PATTERN_DETECTED = "recurring_pattern_detected"
    CLUSTER_GROWTH_DETECTED = "cluster_growth_detected"
    ESCALATION_TRIGGERED = "escalation_triggered"
    CAMPAIGN_CRITICAL = "campaign_critical"
    COORDINATED_ATTACK_DETECTED = "coordinated_attack_detected"
    DEMO_CINEMA_FRAME = "demo_cinema_frame"


class EventEnvelope(BaseModel):
    event: EventName
    correlation_id: UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_id: UUID = Field(default_factory=uuid4)
    agent: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    event_version: str = "1.0"
    schema_hash: str = ""
    producer: str = "hermes-x"
    trace: TraceContext = Field(default_factory=TraceContext)

    def safe_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def governed(self) -> "EventEnvelope":
        if self.schema_hash:
            return self
        return self.model_copy(update={"schema_hash": self.compute_schema_hash()})

    def compute_schema_hash(self) -> str:
        encoded = repr(sorted(self.payload.keys())).encode("utf-8")
        return sha256(encoded).hexdigest()


class AgentStartedEvent(BaseModel):
    investigation_id: str
    agent: str


class AgentProgressEvent(BaseModel):
    investigation_id: str
    agent: str
    message: str


class AgentCompletedEvent(BaseModel):
    investigation_id: str
    agent: str
    duration_ms: int = Field(ge=0)


class ThreatDetectedEvent(BaseModel):
    investigation_id: str
    severity: str
    score: int = Field(ge=0, le=100)
    factors: list[str] = Field(default_factory=list)


class InvestigationCompletedEvent(BaseModel):
    investigation_id: str
    severity: str
    score: int = Field(ge=0, le=100)
