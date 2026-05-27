from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.database.postgres.sql_runner import AsyncSqlRunner
from app.events.models import EventEnvelope


class EventStoreAppendResult(BaseModel):
    event_id: str
    investigation_id: str
    stored: bool = True


class PostgresEventStore:
    def __init__(self, runner: AsyncSqlRunner) -> None:
        self._runner = runner

    async def append(self, investigation_id: str, event: EventEnvelope) -> EventStoreAppendResult:
        governed = event.governed()
        await self._runner.execute(
            """
            INSERT INTO event_log (
                event_id, investigation_id, correlation_id, event_name, event_version,
                schema_hash, producer, agent, payload, trace, occurred_at
            )
            VALUES (
                :event_id, :investigation_id, :correlation_id, :event_name, :event_version,
                :schema_hash, :producer, :agent, :payload, :trace, :occurred_at
            )
            ON CONFLICT (event_id) DO NOTHING
            """,
            {
                "event_id": str(governed.event_id),
                "investigation_id": investigation_id,
                "correlation_id": str(governed.correlation_id),
                "event_name": governed.event.value,
                "event_version": governed.event_version,
                "schema_hash": governed.schema_hash,
                "producer": governed.producer,
                "agent": governed.agent,
                "payload": governed.safe_payload(),
                "trace": governed.trace.model_dump(mode="json"),
                "occurred_at": governed.timestamp.isoformat(),
            },
        )
        return EventStoreAppendResult(event_id=str(governed.event_id), investigation_id=investigation_id)

    async def list_for_investigation(self, investigation_id: str) -> list[EventEnvelope]:
        rows = await self._fetch_rows(
            """
            SELECT payload
            FROM event_log
            WHERE investigation_id = :investigation_id
            ORDER BY occurred_at ASC, sequence_id ASC
            """,
            {"investigation_id": investigation_id},
        )
        return [self._event_from_row(row) for row in rows]

    async def list_for_correlation(self, correlation_id: UUID) -> list[EventEnvelope]:
        rows = await self._fetch_rows(
            """
            SELECT payload
            FROM event_log
            WHERE correlation_id = :correlation_id
            ORDER BY occurred_at ASC, sequence_id ASC
            """,
            {"correlation_id": str(correlation_id)},
        )
        return [self._event_from_row(row) for row in rows]

    async def _fetch_rows(self, statement: str, parameters: dict[str, Any]) -> list[Any]:
        result = await self._runner.execute(statement, parameters)
        if result is None:
            return []
        if hasattr(result, "mappings"):
            return list(result.mappings().all())
        if hasattr(result, "all"):
            return list(result.all())
        return list(result)

    def _event_from_row(self, row: Any) -> EventEnvelope:
        payload = row["payload"] if isinstance(row, dict) else row[0]
        if isinstance(payload, EventEnvelope):
            return payload
        if isinstance(payload, dict):
            return EventEnvelope.model_validate(payload)
        return EventEnvelope.model_validate_json(payload)


class EventStoreHealth(BaseModel):
    reachable: bool
    latency_ms: int = Field(default=0, ge=0)
    detail: str = ""

    @classmethod
    def unavailable(cls, detail: str) -> "EventStoreHealth":
        return cls(reachable=False, detail=detail)
