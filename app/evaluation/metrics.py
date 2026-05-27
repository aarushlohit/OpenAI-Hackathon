from pydantic import BaseModel, Field


class EvaluationMetrics(BaseModel):
    false_positives: int = Field(default=0, ge=0)
    false_negatives: int = Field(default=0, ge=0)
    correlation_precision: float = Field(default=0, ge=0, le=1)
    replay_consistency: float = Field(default=1, ge=0, le=1)
    workflow_latency_ms: int = Field(default=0, ge=0)
    escalation_accuracy: float = Field(default=0, ge=0, le=1)

