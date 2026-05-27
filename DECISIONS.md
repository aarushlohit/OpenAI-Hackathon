# Architecture Decisions

## ADR-001: Provider Access Is Router-Only

Decision: Agents cannot instantiate or call provider clients. Text, vision, audio, and embedding work must go through gateway routers.

Reason: This preserves failover, tracing, schema validation, secret isolation, and future policy enforcement.

## ADR-002: Investigation IDs Are Human-Facing

Decision: Every investigation receives an `INV-XXXXXXXX` ID in addition to a UUID correlation ID.

Reason: Operators need stable readable identifiers, while internal systems still benefit from UUID correlation.

## ADR-003: Circuit Breakers Live in Gateway Infrastructure

Decision: Provider circuit breaker state is owned by the gateway failover core, not by agents or providers.

Reason: Provider health is cross-cutting routing state and should not leak into domain workers.

## ADR-004: Phase 2 Keeps Provider Clients as Isolated Stubs

Decision: Provider classes expose the final modality interfaces but do not yet perform live network calls.

Reason: The architecture can be verified before wiring credentials, retry semantics, and schema-specific provider integrations.

## ADR-005: Agents Produce Evidence, Not Verdicts

Decision: Phase 3 agents return typed evidence contracts. `ThreatScoringEngine` owns final severity.

Reason: Separating evidence generation from scoring keeps decisions explainable, testable, and reviewable.

## ADR-006: OCR Runs Before Vision Analysis

Decision: Vision analysis uses `SafeOCRService` before visual artifact evaluation.

Reason: Recruitment scams often encode payment instructions and impersonation claims in screenshots; sanitized text must be reviewed before multimodal conclusions.

## ADR-007: Graph Intelligence Is Deterministic First

Decision: Phase 6 graph and campaign correlation uses deterministic entity relationships before future embeddings.

Reason: Recruitment scam intelligence must be replayable, auditable, and explainable. Semantic matching can augment correlation later without replacing deterministic lineage.

## ADR-008: Demo Cinema Mode Is Event-Only

Decision: Demo mode emits scripted events through the normal event bus instead of changing investigation results.

Reason: Hackathon reliability should not compromise production investigation contracts or replay integrity.

## ADR-009: Events Are Versioned at the Envelope

Decision: Event version, schema hash, and producer live on `EventEnvelope`.

Reason: Governance must protect all downstream consumers without requiring every producer to manually implement versioning.
