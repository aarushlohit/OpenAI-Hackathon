from pydantic import BaseModel, Field

from app.events.models import EventEnvelope
from app.security.integrity_checks import IntegrityChecks


class AuditReport(BaseModel):
    passed: bool
    findings: list[str] = Field(default_factory=list)


class SecurityAuditMode:
    def __init__(self, checks: IntegrityChecks | None = None) -> None:
        self._checks = checks or IntegrityChecks()

    def audit_events(self, events: list[EventEnvelope]) -> AuditReport:
        findings: list[str] = []
        if not self._checks.verify_append_only_order(events):
            findings.append("event_order_violation")
        if not self._checks.verify_schema_hashes(events):
            findings.append("schema_hash_mismatch")
        return AuditReport(passed=not findings, findings=findings)

