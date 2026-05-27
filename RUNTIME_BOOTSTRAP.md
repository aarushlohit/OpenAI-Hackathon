# Runtime Bootstrap

`RuntimeBootstrap` verifies production readiness without mutating investigations.

Checks:

- schema registry initialized.
- governance registry loaded.
- websocket runtime initialized.
- Redis reachable when configured.
- PostgreSQL reachable when a ping hook is provided.

API:

- `GET /v1/runtime/bootstrap`

Readiness fails closed when required dependencies are degraded.

