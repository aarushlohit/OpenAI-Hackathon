from app.database.postgres.sql_runner import AsyncSqlRunner
from app.replay.snapshot_builder import ReplaySnapshot


class PostgresSnapshotRepository:
    def __init__(self, runner: AsyncSqlRunner) -> None:
        self._runner = runner

    async def save(self, snapshot: ReplaySnapshot) -> None:
        await self._runner.execute(
            """
            INSERT INTO replay_snapshots (
                investigation_id, start_index, end_index, projection_hash, graph_hash,
                timeline_hash, lineage_hash, schema_versions, snapshot_payload
            )
            VALUES (
                :investigation_id, :start_index, :end_index, :projection_hash, :graph_hash,
                :timeline_hash, :lineage_hash, :schema_versions, :snapshot_payload
            )
            """,
            {
                "investigation_id": snapshot.investigation_id,
                "start_index": snapshot.event_range[0],
                "end_index": snapshot.event_range[1],
                "projection_hash": snapshot.projection_hash,
                "graph_hash": snapshot.graph_hash,
                "timeline_hash": snapshot.timeline_hash,
                "lineage_hash": snapshot.investigation_lineage_hash,
                "schema_versions": snapshot.schema_versions,
                "snapshot_payload": snapshot.model_dump(mode="json"),
            },
        )

    async def latest(self, investigation_id: str) -> ReplaySnapshot | None:
        result = await self._runner.execute(
            """
            SELECT snapshot_payload
            FROM replay_snapshots
            WHERE investigation_id = :investigation_id
            ORDER BY created_at DESC
            LIMIT 1
            """,
            {"investigation_id": investigation_id},
        )
        rows = self._rows(result)
        if not rows:
            return None
        payload = rows[0]["snapshot_payload"] if isinstance(rows[0], dict) else rows[0][0]
        if isinstance(payload, dict):
            return ReplaySnapshot.model_validate(payload)
        return ReplaySnapshot.model_validate_json(payload)

    def _rows(self, result) -> list:
        if result is None:
            return []
        if hasattr(result, "mappings"):
            return list(result.mappings().all())
        if hasattr(result, "all"):
            return list(result.all())
        return list(result)
