# Determinism

Hermes-X treats replay determinism as a production primitive.

Components:

- `HashValidator`: validates event and payload hashes.
- `ReplayDeterminismVerifier`: verifies replay consistency and projection hashes.
- `ReplayVerification`: reports verification status, event count, graph hash, projection hash, and duration.
- `SnapshotBuilder`: creates deterministic replay snapshots.
- `SnapshotValidator`: compares replay snapshots.
- `StateFingerprint`: hashes replay, graph, timeline, and lineage state.

Determinism goals:

- Same event ordering.
- Same replay hashes.
- Same graph projection hash.
- Same timeline reconstruction.
- Same snapshot fingerprints.

Phase 9 persistence rules:

- PostgreSQL `event_log` ordering combines event timestamp with append sequence.
- Replay snapshots persist schema versions with projection, graph, timeline, and lineage hashes.
- Cold-start hydration rebuilds projections from event history instead of recomputing agent work.

Phase 10 validation:

- `RuntimeValidator` checks replay verification as part of final operational readiness.
- Websocket payloads include trace and schema metadata so replay clients can validate event ancestry.
- Demo cinema events continue through the normal event bus and remain replayable.
