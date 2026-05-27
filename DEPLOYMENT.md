# Deployment

Phase 9 adds reproducible local deployment foundations with live runtime services.

Files:

- `Dockerfile`
- `docker-compose.yml`
- `deploy/production.env.example`
- `.github/workflows/ci.yml`

Services:

- `api`: FastAPI application and websocket runtime.
- `redis`: realtime fanout, replay pacing, and transient coordination.
- `postgres`: append-only event store, investigations, replay snapshots, lineage, dead letters, and graph projections.
- `neo4j`: optional future graph database.
- `flutter`: optional frontend profile for local web development.

`docker-compose up --build` boots the backend, Redis, PostgreSQL, and optional Neo4j with healthchecks and persistent volumes. Use `docker compose --profile frontend up flutter` when the Flutter SDK container is desired.

Only the API service publishes port `8000` by default. Data services remain internal to the Compose network for safer local boot.

Runtime endpoints:

- `/v1/runtime/health`
- `/v1/runtime/readiness`
- `/v1/runtime/liveness`
- `/v1/runtime/dependencies`
- `/v1/runtime/bootstrap`
- `/v1/providers/capabilities`

Validation:

- `python scripts/final_runtime_validation.py --json`
- `python scripts/final_runtime_validation.py --strict`
- `python scripts/validate_live_providers.py`

MVP scripts:

- `./scripts/dev_bootstrap.sh`
- `./scripts/start_hermes.sh`
- `./scripts/demo_mode.sh telegram_onboarding_scam`
- `./scripts/reset_runtime.sh`
