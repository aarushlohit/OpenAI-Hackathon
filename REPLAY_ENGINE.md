# Replay Engine

The replay engine reconstructs a historical investigation from persisted event history.

Goals:

- Forensic playback.
- Demo mode.
- Audit review.
- Training mode.

Current implementation:

- `ReplayEngine` loads events from `InvestigationRepository`.
- Events are converted to ordered `ReplayFrame` records.
- Each frame includes an index and offset from the first event.
- Each frame includes an integrity hash derived from the serialized event.
- Replay supports stepping by frame index.
- Future UI clients can step through frames or stream them on a timer.

Integrity rule:

Replay is derived from stored events. It does not re-run agents or recompute threat scores.

Tamper detection:

`ReplayEngine.verify()` checks frame hashes against event payloads before replay is trusted.

Phase 8 determinism:

`ReplayDeterminismVerifier` produces `ReplayVerification` with projection hash, graph hash, event count, and verification duration.

Phase 8.5 snapshots:

`SnapshotBuilder` produces immutable replay snapshots containing event range, projection hash, graph hash, timeline hash, lineage hash, and schema versions.

Graph replay:

Graph state is rebuildable from context snapshots and graph events such as `graph_node_added`, `graph_edge_added`, `campaign_detected`, and `entity_correlated`.

Phase 9 persistence:

- `PostgresEventStore` reconstructs replay inputs from `event_log` ordered by `occurred_at` and `sequence_id`.
- `PostgresSnapshotRepository` stores immutable replay snapshot payloads and schema version maps.
- `EventStoreHydrator` supports cold-start projection hydration from persisted events and context.

Phase 10 convergence:

- Runtime validation verifies replay sessions before demo readiness is trusted.
- Websocket event payloads carry schema and trace metadata required for replay-aware clients.
- Failure simulations include replay interruption checks that must preserve verification status.
