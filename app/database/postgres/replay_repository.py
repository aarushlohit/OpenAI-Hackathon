from app.database.postgres.event_store import PostgresEventStore
from app.memory.investigation_repository import InvestigationRepository
from app.replay.replay_engine import ReplayEngine, ReplaySession


class PostgresReplayRepository:
    def __init__(self, event_store: PostgresEventStore, repository: InvestigationRepository) -> None:
        self._event_store = event_store
        self._replay_engine = ReplayEngine(repository)

    async def rebuild(self, investigation_id: str, speed: float = 1.0) -> ReplaySession:
        return await self._replay_engine.build(investigation_id, speed=speed)

    async def event_count(self, investigation_id: str) -> int:
        events = await self._event_store.list_for_investigation(investigation_id)
        return len(events)

