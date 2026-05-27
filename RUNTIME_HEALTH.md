# Runtime Health

Hermes-X runtime health reports operational readiness without mutating investigations.

Endpoints:

- `/v1/runtime/health`
- `/v1/runtime/readiness`
- `/v1/runtime/liveness`
- `/v1/runtime/dependencies`

Tracked signals:

- websocket health.
- replay latency.
- provider/dependency configuration.
- queue pressure hooks.
- investigation throughput hooks.

