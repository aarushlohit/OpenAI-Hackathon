# Architecture

Hermes-X follows clean architecture with explicit inward dependencies.

Layers:

- `terminal`: operator-facing CLI and rendering.
- `api`: FastAPI transport layer.
- `websocket`: realtime investigation event streaming, replay subscription, and websocket serialization boundary.
- `replay`: historical event playback engine.
- `reporting`: terminal-friendly and export-ready investigation report models.
- `graph`: deterministic threat graph projection and repository abstraction.
- `intelligence`: correlation, campaign detection, and similarity engines.
- `autonomous`: monitoring, alerting, and scheduling for operational cyber defense flows.
- `demo`: cinema-mode scenarios and scripted event pacing.
- `governance`: agent contracts, permissions, policies, and risk thresholds.
- `evaluation`: benchmark scenarios and replay consistency metrics.
- `archive`: retention policies and event compression.
- `tools`: MCP-ready tool registry abstraction.
- `runtime`: health, readiness, liveness, and dependency diagnostics.
- `diagnostics`: replay and graph inspection.
- `sandbox`: isolated replay and evaluation execution.
- `agents`: use-case orchestration and autonomous workers.
- `scoring`: threat scoring and final severity assembly.
- `services`: deterministic intelligence services used by agents.
- `prompts`: versioned prompt assets for future model-backed services.
- `gateway`: provider-neutral AI routing and failover.
- `observability`: provider metrics, latency traces, and circuit breaker state.
- `events`: structured event envelopes and event bus.
- `database`: production PostgreSQL adapters for event sourcing and replay persistence.
- `memory`: persistence contracts for investigation memory.
- `security`: zero-trust intake and runtime policies.
- `schemas`: Pydantic contracts shared across boundaries.
- `models`: shared domain value objects.
- `core`: settings, dependency composition, and application errors.

Phase 2+ keeps in-memory event and memory implementations for local execution while establishing the final gateway surface for text, vision, audio, and embeddings. PostgreSQL, Neo4j, and Redis are represented in configuration and documented for durable adapters.

Phase 3 adds autonomous intelligence agents for behavior analysis, OSINT, and OCR-first vision analysis. Agents return typed results and the threat engine owns final severity.

Phase 4 adds workflow-driven parallel orchestration, shared investigation context, entity extraction, event replay memory, and resilient partial-failure handling.

Phase 5 adds the cyber intelligence experience layer: typed websocket delivery, replay-safe subscriptions, graph projection foundations, export snapshots, and a Flutter client scaffold that consumes backend events only.

Phase 6 adds graph-native threat memory, scam campaign correlation, realtime graph events, protection API endpoints, and the Hermes Sentinel browser extension scaffold.

Phase 7 adds autonomous monitoring, continuous threat feeds, demo cinema mode, storytelling projections, replay integrity hashing, lineage contracts, and SOC-facing UI panels.

Phase 8 adds schema governance, event versioning, replay determinism verification, agent contracts, evaluation scaffolding, deployment foundations, security audit mode, archival policies, and MCP-ready tool registration.

Phase 8.5 adds deterministic replay snapshots, trace context, runtime health APIs, dead-letter queues, backpressure controls, sandbox replay, diagnostics, and safe failover controls.

Phase 9 adds infrastructure convergence: PostgreSQL adapters for append-only events, investigations, snapshots, replay history, dead letters, and graph projections; Redis runtime primitives for websocket fanout and bounded realtime coordination; bootstrap readiness checks; provider HTTP normalization; and Docker orchestration for the API, Redis, PostgreSQL, optional Neo4j, and frontend development runtime.

Phase 10 adds operational activation: provider capability registry, environment-driven multimodal routing, NVIDIA Gemma 3n fallback defaults, Pollinations OpenAI-compatible fallback, websocket schema/trace enrichment, final runtime validation, and failure simulation scaffolding for demo readiness.

Dependency rule:

Transport layers depend inward on use cases. Agents depend on gateway abstractions, event contracts, and repositories. Providers stay behind routers.

Provider routing:

- Text: OpenAI, NVIDIA Gemma 3n, Pollinations emergency fallback.
- Vision: OpenAI Vision, NVIDIA Gemma 3n, Pollinations Vision.
- Audio: OpenAI Audio, NVIDIA Gemma 3n.
- Embeddings: OpenAI, Pollinations.
