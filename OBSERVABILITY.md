# Observability

Hermes-X observability covers structured events, request tracing, provider metrics, latency tracking, failover analytics, and investigation replay.

Current capabilities:

- Every investigation has an `INV-XXXXXXXX` ID.
- Every event has a UUID `correlation_id` and `event_id`.
- Provider attempts record operation, provider, latency, success, and failure reason.
- Agent attempts record agent name, latency, success, and investigation ID.
- Provider metrics are available through `/v1/observability/provider-metrics`.
- Agent metrics are available through `/v1/observability/agent-metrics`.
- Provider failures emit `provider_failed`.
- Fallback routing emits `provider_failover`.
- Agent progress emits `agent_progress`.
- Realtime stream boundaries are isolated under `app/websocket`.
- Websocket subscribers receive replay-safe serialized events.
- Replay sessions expose ordered frames for audit review.
- Flutter renders observability state without owning metrics logic.
- Graph metrics track projections, node growth, edge growth, campaign detections, and extension alerts.
- Graph metrics are available through `/v1/observability/graph-metrics`.
- Graph metrics also track autonomous alerts, replay verifications, and workflow latency totals.
- Threat feed items expose autonomous operational activity through `/v1/threat-feed`.
- Replay verification reports event count, graph hash, projection hash, and duration.
- Evaluation metrics track replay consistency and workflow latency.
- Runtime health exposes liveness, readiness, dependencies, websocket health, and replay latency.
- Trace context is carried on every event envelope.
- Dead-letter queues preserve malformed event diagnostics.

Phase 9 capabilities:

- Durable event replay from PostgreSQL.
- Redis-backed live event streams.
- Runtime bootstrap checks for schema registry, governance registry, websocket runtime, Redis, and PostgreSQL hooks.
- Runtime metrics record Redis publishes, PostgreSQL writes, replay hydrations, websocket reconnects, provider failovers, and latency samples.

Phase 10 capabilities:

- Provider capability registry is exposed through `/v1/providers/capabilities`.
- Websocket payloads include event version, schema hash, producer, and trace context.
- Final runtime validation checks bootstrap, websocket streaming, replay determinism, provider capabilities, and graph projection initialization.

Planned capabilities:

- OpenTelemetry trace export.
- Provider cost and token analytics.
- Alerting for sustained circuit breaker openings.
- Threat score distribution dashboards.
- Protection API latency histograms.
- Websocket subscriber load and replay timing histograms.
- Event throughput and schema drift dashboards.
