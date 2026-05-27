CREATE TABLE IF NOT EXISTS investigations (
    investigation_id TEXT PRIMARY KEY,
    correlation_id UUID NOT NULL,
    evidence_kind TEXT NOT NULL,
    raw_input TEXT NOT NULL,
    context_payload JSONB NOT NULL,
    verdict_payload JSONB,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS event_log (
    sequence_id BIGSERIAL PRIMARY KEY,
    event_id UUID NOT NULL UNIQUE,
    investigation_id TEXT NOT NULL,
    correlation_id UUID NOT NULL,
    event_name TEXT NOT NULL,
    event_version TEXT NOT NULL,
    schema_hash TEXT NOT NULL,
    producer TEXT NOT NULL,
    agent TEXT,
    payload JSONB NOT NULL,
    trace JSONB NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS event_log_investigation_order_idx
    ON event_log (investigation_id, occurred_at, sequence_id);

CREATE INDEX IF NOT EXISTS event_log_correlation_order_idx
    ON event_log (correlation_id, occurred_at, sequence_id);

CREATE TABLE IF NOT EXISTS replay_snapshots (
    snapshot_id BIGSERIAL PRIMARY KEY,
    investigation_id TEXT NOT NULL,
    start_index INTEGER NOT NULL,
    end_index INTEGER NOT NULL,
    projection_hash TEXT NOT NULL,
    graph_hash TEXT NOT NULL,
    timeline_hash TEXT NOT NULL,
    lineage_hash TEXT NOT NULL,
    schema_versions JSONB NOT NULL,
    snapshot_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lineage (
    lineage_id BIGSERIAL PRIMARY KEY,
    investigation_id TEXT NOT NULL,
    parent_investigation_id TEXT,
    relationship TEXT NOT NULL,
    lineage_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dead_letter_events (
    dead_letter_id BIGSERIAL PRIMARY KEY,
    event_id UUID,
    investigation_id TEXT,
    reason TEXT NOT NULL,
    payload JSONB NOT NULL,
    trace JSONB,
    quarantined_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS graph_projections (
    investigation_id TEXT PRIMARY KEY,
    projection_payload JSONB NOT NULL,
    projection_hash TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
