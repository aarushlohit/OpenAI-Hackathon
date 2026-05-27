# PostgreSQL Event Store

PostgreSQL is the durable source of truth for Hermes-X investigations.

Tables:

- `investigations`: typed context, raw intake summary, and final verdict payloads.
- `event_log`: append-only governed event envelopes ordered by `occurred_at` and `sequence_id`.
- `replay_snapshots`: immutable deterministic replay snapshots.
- `lineage`: parent-child investigation relationships.
- `dead_letter_events`: quarantined malformed or unauthorized events.
- `graph_projections`: deterministic graph projection payloads.

Adapters:

- `PostgresEventStore`
- `PostgresInvestigationRepository`
- `PostgresSnapshotRepository`
- `PostgresReplayRepository`
- `PostgresGraphProjectionRepository`

Events are inserted with `ON CONFLICT (event_id) DO NOTHING` to preserve idempotency without mutating existing history.

