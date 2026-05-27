# API Contracts

Base path: `/v1`

`GET /v1/health`

Response:

```json
{"status": "ok"}
```

`POST /v1/investigations`

Request:

```json
{
  "raw_input": "https://example.com/internship",
  "kind": "url",
  "investigation_id": "INV-1A2B3C4D",
  "source_url": null
}
```

Response:

```json
{
  "investigation_id": "INV-1A2B3C4D",
  "correlation_id": "uuid",
  "finding": {
    "summary": "string",
    "risk_level": "medium",
    "evidence": [],
    "recommended_actions": []
  },
  "completed_at": "timestamp"
}
```

All external responses must remain Pydantic-validated.

`GET /v1/observability/provider-metrics`

Response:

```json
{
  "text_generation:openai": {
    "calls": 10,
    "failures": 1,
    "avg_latency_ms": 820
  }
}
```

`GET /v1/observability/agent-metrics`

Response:

```json
{
  "behavior": {
    "calls": 10,
    "failures": 0,
    "avg_latency_ms": 3
  }
}
```

`GET /v1/observability/graph-metrics`

Returns graph projection, node, edge, campaign, and extension alert counters.

`GET /v1/observability/runtime-metrics`

Returns Redis publish counts, PostgreSQL write counters, replay hydration counts, websocket reconnect counters, provider failover counters, and latency samples.

`GET /v1/threat-feed`

Returns the latest autonomous threat feed items.

`GET /v1/demo/scenarios`

Returns available demo cinema scenarios.

Structured API errors use:

```json
{
  "code": "rate_limited",
  "message": "Request quota exceeded"
}
```

Runtime APIs:

- `GET /v1/runtime/health`
- `GET /v1/runtime/readiness`
- `GET /v1/runtime/liveness`
- `GET /v1/runtime/dependencies`
- `GET /v1/runtime/bootstrap`

`GET /v1/runtime/bootstrap` returns startup readiness checks:

```json
{
  "ready": false,
  "checks": [
    {"name": "schema_registry", "status": "ok", "required": true, "detail": ""}
  ]
}
```

Future realtime transport:

- WebSocket clients consume investigation events by correlation ID.
- Flutter remains a presentation layer and must not own orchestration or scoring logic.

`GET /v1/investigations/{investigation_id}/events`

Returns serialized event history for audit and UI recovery.

`GET /v1/investigations/{investigation_id}/replay`

Returns ordered replay frames with event offsets.

`GET /v1/investigations/{investigation_id}/context`

Returns the latest stored investigation context.

WebSocket:

`/v1/ws/investigations/{correlation_id}`

Streams replay-safe event payloads for live and reconnecting clients.

Protection API:

- `GET /v1/protection/domain/{domain}`
- `GET /v1/protection/recruiter/{email}`
- `GET /v1/protection/telegram/{handle}`
- `GET /v1/protection/upi/{upi_id}`
- `GET /v1/protection/graph/{investigation_id}`

Protection lookup response:

```json
{
  "entity": "fake.example",
  "entity_type": "domain",
  "risk": "elevated",
  "related_investigations": ["INV-ABCDEF12"]
}
```
