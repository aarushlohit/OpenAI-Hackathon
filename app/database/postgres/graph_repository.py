from hashlib import sha256

from app.database.postgres.sql_runner import AsyncSqlRunner
from app.graph.projections import ThreatGraphProjection
from app.graph.repositories.graph_repository import GraphRepository


class PostgresGraphProjectionRepository(GraphRepository):
    def __init__(self, runner: AsyncSqlRunner) -> None:
        self._runner = runner

    async def save_projection(self, projection: ThreatGraphProjection) -> None:
        payload = projection.model_dump(mode="json")
        await self._runner.execute(
            """
            INSERT INTO graph_projections (investigation_id, projection_payload, projection_hash)
            VALUES (:investigation_id, :projection_payload, :projection_hash)
            ON CONFLICT (investigation_id)
            DO UPDATE SET projection_payload = EXCLUDED.projection_payload,
                          projection_hash = EXCLUDED.projection_hash,
                          updated_at = NOW()
            """,
            {
                "investigation_id": projection.investigation_id,
                "projection_payload": payload,
                "projection_hash": sha256(projection.model_dump_json().encode("utf-8")).hexdigest(),
            },
        )

    async def get_projection(self, investigation_id: str) -> ThreatGraphProjection | None:
        result = await self._runner.execute(
            "SELECT projection_payload FROM graph_projections WHERE investigation_id = :investigation_id",
            {"investigation_id": investigation_id},
        )
        rows = self._rows(result)
        if not rows:
            return None
        payload = rows[0]["projection_payload"] if isinstance(rows[0], dict) else rows[0][0]
        if isinstance(payload, dict):
            return ThreatGraphProjection.model_validate(payload)
        return ThreatGraphProjection.model_validate_json(payload)

    async def all_projections(self) -> list[ThreatGraphProjection]:
        result = await self._runner.execute(
            "SELECT projection_payload FROM graph_projections ORDER BY updated_at ASC"
        )
        return [self._projection_from_payload(self._payload(row)) for row in self._rows(result)]

    def _rows(self, result) -> list:
        if result is None:
            return []
        if hasattr(result, "mappings"):
            return list(result.mappings().all())
        if hasattr(result, "all"):
            return list(result.all())
        return list(result)

    def _payload(self, row):
        return row["projection_payload"] if isinstance(row, dict) else row[0]

    def _projection_from_payload(self, payload) -> ThreatGraphProjection:
        if isinstance(payload, dict):
            return ThreatGraphProjection.model_validate(payload)
        return ThreatGraphProjection.model_validate_json(payload)

