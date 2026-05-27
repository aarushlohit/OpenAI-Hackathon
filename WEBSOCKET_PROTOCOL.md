# WebSocket Protocol

Endpoint:

`/v1/ws/investigations/{correlation_id}`

Delivery model:

- Multiple subscribers are supported.
- Each subscriber receives an isolated event stream.
- Reconnects replay stored events for the correlation ID.
- Events are serialized through `EventSerializer`.
- Malformed websocket payloads are rejected before rendering.

Payload:

```json
{
  "event": "agent_progress",
  "correlation_id": "uuid",
  "timestamp": "2026-05-27T00:00:00Z",
  "event_id": "uuid",
  "agent": "behavior",
  "payload": {
    "investigation_id": "INV-ABCDEF12",
    "message": "Payment coercion detected"
  }
}
```

Supported event names:

- `investigation_started`
- `investigation_progress`
- `agent_started`
- `agent_progress`
- `agent_completed`
- `threat_detected`
- `provider_failover`
- `investigation_completed`
- `investigation_replay`
- `graph_node_added`
- `graph_edge_added`
- `campaign_detected`
- `entity_correlated`
- `threat_feed_update`
- `recurring_pattern_detected`
- `escalation_triggered`
- `coordinated_attack_detected`
- `demo_cinema_frame`

Graph events are server-authored only. Clients must render them as projections and must not infer or submit relationship decisions.
