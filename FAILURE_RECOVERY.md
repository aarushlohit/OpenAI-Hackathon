# Failure Recovery

Hermes-X handles runtime failures through bounded degradation.

Scenarios:

- Redis unavailable: websocket fanout degrades while append-only events remain durable in PostgreSQL.
- PostgreSQL unavailable: readiness fails and live investigations should not be accepted in production mode.
- Provider outage: gateway failover routes through configured providers and circuit breakers.
- Replay interruption: persisted events and replay snapshots allow reconstruction.
- Malformed events: dead-letter queues quarantine payloads for audit visibility.
- OpenAI outage: capability routing fails over to NVIDIA Gemma 3n, then Pollinations where supported.
- NVIDIA outage: routing falls back to the next configured provider when the modality supports it.
- Websocket reconnect storms: bounded subscription queues prevent unbounded memory growth.

Recovery principle:

Never mutate historical events to repair runtime state. Rebuild projections from immutable history.
