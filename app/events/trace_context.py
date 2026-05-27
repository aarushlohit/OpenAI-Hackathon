from uuid import uuid4

from pydantic import BaseModel, Field


class TraceContext(BaseModel):
    trace_id: str = Field(default_factory=lambda: uuid4().hex)
    parent_span_id: str | None = None
    span_id: str = Field(default_factory=lambda: uuid4().hex[:16])
    replay_trace: str | None = None
    workflow_trace: str | None = None

    def child(self) -> "TraceContext":
        return TraceContext(
            trace_id=self.trace_id,
            parent_span_id=self.span_id,
            replay_trace=self.replay_trace,
            workflow_trace=self.workflow_trace,
        )

