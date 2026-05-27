# Memory System

Hermes-X memory is divided into case memory, entity memory, graph memory, and operational memory.

Case memory stores investigation events, findings, evidence, and operator decisions. PostgreSQL is the authoritative store for immutable case records.

Entity memory stores recruiters, companies, domains, phone numbers, Telegram handles, email addresses, and document fingerprints. Neo4j represents relationships and repeated scam infrastructure.

Operational memory stores short-lived queues, locks, deduplication keys, and streaming state. Redis is the preferred backend.

Current implementation:

- `MemoryRepository` defines append and case-list operations.
- `InMemoryMemoryRepository` is a local Phase 1 adapter.
- Stored values must be Pydantic-validated before persistence.
- Investigation records include both `INV-XXXXXXXX` operator IDs and UUID correlation IDs.

Phase 2 direction:

- Persist event streams for replay.
- Store provider traces for failover analytics.
- Store normalized entity memory separately from raw artifacts.

Phase 3 memory records:

- Store typed agent results under investigation memory.
- Store threat scores separately from agent evidence.
- Preserve agent explanations for replay and human review.

Phase 4 and 5 memory:

- Investigation events are retained for replay subscriptions.
- Context snapshots preserve extracted entities and agent findings.
- Replay sessions are derived from persisted events, not recomputed agent work.
- UI clients consume exported snapshots and websocket events without writing memory state.

Phase 6 threat memory:

- Graph projections are stored through a graph repository abstraction.
- Entity index maps domains, handles, UPI IDs, and other indicators to investigations.
- Threat memory enriches protection API lookups and campaign correlation.
- Future Neo4j migration should replace adapters, not orchestration contracts.

Phase 7 operational memory:

- Threat feed items are append-only operational intelligence records.
- Replay frames include integrity hashes for tamper detection.
- Lineage models represent parent-child investigations and inherited evidence.
- Autonomous monitoring reads threat memory and emits events; it does not mutate prior investigations.

Phase 8 governed memory:

- Event envelopes carry version, producer, and schema hash.
- Replay verification records event counts and projection hashes.
- Retention policies define future event and replay snapshot archival windows.
- Archive compression is available for serialized event payloads.

Phase 9 persistence convergence:

- PostgreSQL event log is the durable append-only source of truth.
- `PostgresEventStore` writes governed envelopes and reconstructs events by investigation or correlation ID.
- `PostgresInvestigationRepository` persists typed context and verdict records while event history remains append-only.
- Replay snapshots and graph projections have PostgreSQL adapters for cold-start hydration and deterministic rebuilds.
- Redis is transient operational memory for fanout and coordination; it does not replace the event store.
