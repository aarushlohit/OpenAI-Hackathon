# Docker Boot

Boot Hermes-X:

```bash
docker compose up --build
```

Services:

- `api`
- `postgres`
- `redis`
- `neo4j`

Only the API publishes a host port by default. Redis, PostgreSQL, and Neo4j stay on the Compose network to avoid host port conflicts.

Optional Flutter web runtime:

```bash
docker compose --profile frontend up flutter
```

PostgreSQL initializes with `app/database/postgres/migrations/001_initial.sql`.

The API healthcheck calls `/v1/runtime/liveness`. Runtime readiness should be checked through `/v1/runtime/bootstrap`.
