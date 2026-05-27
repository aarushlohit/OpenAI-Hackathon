# Event Schema

Every event uses `EventEnvelope`.

Fields:

- `event`: controlled event name.
- `event_version`: semantic event schema version.
- `schema_hash`: hash of the payload schema keys.
- `producer`: event producer name.
- `trace`: trace context containing trace ID, span ID, parent span ID, replay trace, and workflow trace.
- `correlation_id`: investigation-level UUID.
- `timestamp`: UTC event timestamp.
- `event_id`: unique event UUID.
- `agent`: optional agent name.
- `payload`: event-specific JSON object.
- `investigation_id`: included inside payload for operator-facing investigation events.

Example:

```json
{
  "event": "agent_started",
  "agent": "intake",
  "timestamp": "2026-05-27T00:00:00Z",
  "correlation_id": "uuid",
  "event_id": "uuid",
  "payload": {}
}
```

Event names are defined in `app/events/models.py`.

Standard lifecycle events:

- `agent_started`
- `agent_progress`
- `agent_completed`
- `agent_failed`
- `threat_detected`
- `provider_failed`
- `provider_failover`
- `investigation_completed`
- `investigation_replay`
- `graph_node_added`
- `graph_edge_added`
- `campaign_detected`
- `entity_correlated`
- `threat_feed_update`
- `campaign_expanded`
- `autonomous_alert`
- `recurring_pattern_detected`
- `cluster_growth_detected`
- `escalation_triggered`
- `campaign_critical`
- `coordinated_attack_detected`
- `demo_cinema_frame`

WebSocket serialization uses the same envelope fields and validates them with `WebsocketEventPayload`.

Events are governed by `SchemaRegistry` and compatibility checks.

Phase 9 persistence rules:

- Persisted event rows must include event version, schema hash, producer, trace context, correlation ID, and occurrence timestamp.
- Replay queries order by `occurred_at` and database `sequence_id` to preserve deterministic reconstruction.
- Redis fanout messages serialize the same governed envelope and are not treated as durable truth.
