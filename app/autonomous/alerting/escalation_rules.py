from pydantic import BaseModel, Field


class AlertEscalation(BaseModel):
    event: str
    severity: str
    reason: str = Field(min_length=1)
    related_investigations: list[str] = Field(default_factory=list)


class EscalationRules:
    def evaluate(self, entity: str, related_investigations: list[str]) -> AlertEscalation | None:
        count = len(related_investigations)
        if count >= 3:
            return AlertEscalation(
                event="coordinated_attack_detected",
                severity="critical",
                reason=f"{entity} appears in {count} investigations",
                related_investigations=related_investigations,
            )
        if count >= 2:
            return AlertEscalation(
                event="escalation_triggered",
                severity="high",
                reason=f"{entity} is reused across investigations",
                related_investigations=related_investigations,
            )
        return None

