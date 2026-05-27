# Session Log

## 2026-05-27

Phase 2+ baseline alignment:

- Added unified `ProviderResponse` contract.
- Added failover router core with retry loops, circuit breaker checks, and provider metrics.
- Added audio and embedding router surfaces.
- Extended final provider hierarchy to OpenAI, NVIDIA NIM, and Pollinations where applicable.
- Added `INV-XXXXXXXX` investigation IDs.
- Added missing continuity docs: `DECISIONS.md`, `STYLE_GUIDE.md`, and `OBSERVABILITY.md`.

Phase 3 autonomous intelligence layer:

- Added `BehaviorAnalysisAgent`, `OSINTAgent`, and `VisionAnalysisAgent`.
- Added deterministic services for behavior signals, WHOIS profile hints, reputation checks, scam lookup, and safe OCR.
- Added `ThreatScoringEngine` and typed result contracts.
- Added prompt registry and versioned prompt files.
- Added agent metrics and realtime terminal panels.
- Added focused tests for behavior analysis, OCR, malformed AI output, scoring, and failover.

Phase 4 orchestration foundation:

- Added workflow routing, shared context, entity extraction, parallel engine execution, event replay memory, and partial-failure handling.
- Added websocket replay boundary and tests for workflow, extraction, memory, streaming, and graph projection.

Phase 5 experience layer:

- Added typed websocket manager, subscription registry, event serializer, and FastAPI websocket endpoint.
- Added replay engine, graph projection foundation, context/event/replay API endpoints, and export-ready report snapshots.
- Added Flutter scaffold under `frontend/flutter_app` with immutable event models, websocket repository, timeline panel, dashboard shell, graph canvas, and SOC-style theme.

Phase 6 graph intelligence and Sentinel:

- Added threat graph engine, node/edge builders, relationship rules, and graph repository abstraction.
- Added deterministic campaign detection, entity similarity, threat memory, and entity index.
- Added graph websocket events, graph metrics, and protection API endpoints for domain, recruiter, Telegram, and UPI lookups.
- Added Hermes Sentinel Manifest V3 scaffold with URL scanning and warning overlay.
- Added tests for graph projection, correlation, entity matching, extension contract, and protection lookup.

Phase 7 autonomous operations and cinema mode:

- Added autonomous monitor engine, entity watcher, scheduler, escalation rules, and continuous threat feed.
- Added demo cinema mode scenarios and `demo_cinema_frame` event support.
- Added storytelling and executive reporting projections.
- Added replay integrity hashes, replay stepping, lineage model, and SOC-style Flutter panels.
- Added tests for autonomous monitoring, escalation, replay integrity, and storytelling.

Phase 8 governed platform hardening:

- Added schema registry, event versions, compatibility checks, event schema hashes, and producers.
- Added replay determinism verifier and hash validator.
- Added governance policies, contract registry, risk thresholds, and `AGENT_CONTRACT.yaml`.
- Added evaluation framework, archive utilities, MCP-ready tool registry, API rate limiter, websocket authorizer, and security audit mode.
- Added Docker, Compose, production env example, and CI workflow.
- Added tests for contracts, governance, determinism, load resilience, deployment files, and evaluation.

Phase 8.5 deployable runtime:

- Added replay snapshots, snapshot validation, state fingerprints, and trace context.
- Added runtime health subsystem, dependency monitor, runtime APIs, diagnostics, sandbox replay, dead-letter queue, and failover controls.
- Added websocket backpressure limit and health/readiness/liveness endpoints.
- Added tests for snapshots, dead-letter quarantine, tracing, runtime health, diagnostics, and failover controls.

Phase 9 infrastructure convergence:

- Added PostgreSQL persistence adapters for append-only events, investigations, replay snapshots, replay rebuilds, and graph projections.
- Added initial PostgreSQL migration for investigations, event log, snapshots, lineage, dead letters, and graph projection tables.
- Added Redis runtime primitives for namespace-safe pub/sub, event broadcast, and websocket subscription fanout.
- Added runtime bootstrap checks, event-store hydration, runtime metrics, database integrity checks, and Redis channel validation.
- Wired providers to real HTTP transport boundaries with normalized responses and fail-closed credential behavior.
- Expanded Docker Compose with healthchecks, persistent volumes, API, Redis, PostgreSQL, optional Neo4j, and optional Flutter web runtime.

Phase 10 operational activation:

- Added provider capability registry, provider priority resolver, and unified multimodal router facade.
- Updated NVIDIA NIM defaults to `google/gemma-3n-e2b-it` for text, vision, and audio fallback.
- Added Pollinations OpenAI-compatible chat completion fallback for text and vision.
- Added websocket schema and trace enrichment for live clients.
- Added final runtime validation script and failure simulation scaffolding.
- Added final docs for multimodal routing, demo flow, provider failover, provider setup, Docker boot, runtime validation, and operational playbook.
