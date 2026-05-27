# Database Schema

PostgreSQL planned tables:

- `investigations`: case identity, status, risk level, timestamps.
- `evidence_items`: normalized evidence with confidence and source.
- `agent_events`: immutable event log.
- `artifacts`: references to quarantined uploads and derived metadata.
- `provider_calls`: model, provider, latency, failure reason, and cost metadata.

Neo4j planned nodes:

- `Recruiter`
- `Company`
- `Domain`
- `Email`
- `Phone`
- `TelegramHandle`
- `DocumentFingerprint`
- `ScamCampaign`

Redis planned keys:

- investigation stream buffers.
- provider circuit breaker state.
- rate-limit counters.
- idempotency keys.

Phase 1 uses repository interfaces and in-memory adapters only.

