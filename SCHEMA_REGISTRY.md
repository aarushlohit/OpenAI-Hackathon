# Schema Registry

Events are versioned and hash-governed.

Each event envelope includes:

- `event_version`
- `schema_hash`
- `producer`
- `timestamp`

Components:

- `SchemaRegistry`: registers event schema hashes.
- `CompatibilityChecker`: checks backward-compatible field evolution.
- `event_versions.py`: records the current event version map.

Schema governance protects websocket consumers, replay verification, and deterministic projections from drift.

