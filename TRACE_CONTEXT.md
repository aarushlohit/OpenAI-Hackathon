# Trace Context

Trace context links events, websocket messages, graph mutations, provider calls, and replay operations.

Fields:

- `trace_id`
- `parent_span_id`
- `span_id`
- `replay_trace`
- `workflow_trace`

Every `EventEnvelope` carries trace context by default. Child spans preserve the trace ID and reference the parent span.

