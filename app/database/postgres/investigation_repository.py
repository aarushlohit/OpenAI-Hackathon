from app.database.postgres.event_store import PostgresEventStore
from app.database.postgres.sql_runner import AsyncSqlRunner
from app.events.models import EventEnvelope
from app.memory.investigation_repository import InvestigationRepository
from app.models.investigation_context import InvestigationContext
from app.models.threat_score import ThreatScore


class PostgresInvestigationRepository(InvestigationRepository):
    def __init__(self, runner: AsyncSqlRunner, event_store: PostgresEventStore) -> None:
        self._runner = runner
        self._event_store = event_store

    async def save_context(self, context: InvestigationContext) -> None:
        await self._runner.execute(
            """
            INSERT INTO investigations (
                investigation_id, correlation_id, evidence_kind, raw_input,
                context_payload, created_at, updated_at
            )
            VALUES (
                :investigation_id, :correlation_id, :evidence_kind, :raw_input,
                :context_payload, :created_at, :updated_at
            )
            ON CONFLICT (investigation_id)
            DO UPDATE SET context_payload = EXCLUDED.context_payload,
                          updated_at = EXCLUDED.updated_at
            """,
            {
                "investigation_id": context.investigation_id,
                "correlation_id": str(context.correlation_id),
                "evidence_kind": context.evidence_kind,
                "raw_input": context.raw_input,
                "context_payload": context.model_dump(mode="json"),
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
            },
        )

    async def load_context(self, investigation_id: str) -> InvestigationContext | None:
        result = await self._runner.execute(
            "SELECT context_payload FROM investigations WHERE investigation_id = :investigation_id",
            {"investigation_id": investigation_id},
        )
        rows = self._rows(result)
        if not rows:
            return None
        payload = rows[0]["context_payload"] if isinstance(rows[0], dict) else rows[0][0]
        if isinstance(payload, dict):
            return InvestigationContext.model_validate(payload)
        return InvestigationContext.model_validate_json(payload)

    async def append_event(self, investigation_id: str, event: EventEnvelope) -> None:
        await self._event_store.append(investigation_id, event)

    async def list_events(self, investigation_id: str) -> list[EventEnvelope]:
        return await self._event_store.list_for_investigation(investigation_id)

    async def save_verdict(self, investigation_id: str, verdict: ThreatScore) -> None:
        await self._runner.execute(
            """
            UPDATE investigations
            SET verdict_payload = :verdict_payload, updated_at = NOW()
            WHERE investigation_id = :investigation_id
            """,
            {"investigation_id": investigation_id, "verdict_payload": verdict.model_dump(mode="json")},
        )

    def _rows(self, result) -> list:
        if result is None:
            return []
        if hasattr(result, "mappings"):
            return list(result.mappings().all())
        if hasattr(result, "all"):
            return list(result.all())
        return list(result)

