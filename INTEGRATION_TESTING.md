# Integration Testing

Phase 9 integration tests validate infrastructure contracts without requiring local services by using fake runners and clients.

Covered contracts:

- PostgreSQL append-only event writes.
- PostgreSQL replay query ordering.
- Redis namespace validation and publish behavior.
- Runtime bootstrap readiness checks.
- Event-store hydration behavior.
- Provider fail-closed activation.

Future service-backed suites should run against Docker Compose with PostgreSQL and Redis enabled.

