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

