# Snapshot System

Replay snapshots certify deterministic investigation state.

Snapshot fields:

- event range.
- projection hash.
- graph hash.
- timeline hash.
- investigation lineage hash.
- schema versions.

Components:

- `SnapshotBuilder`
- `SnapshotValidator`
- `StateFingerprint`

Snapshots are immutable and derived from replay sessions plus deterministic projections.

