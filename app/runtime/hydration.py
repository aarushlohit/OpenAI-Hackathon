from pydantic import BaseModel, Field

from app.graph.graph_engine import ThreatGraphEngine
from app.memory.investigation_repository import InvestigationRepository


class HydrationReport(BaseModel):
    investigation_id: str
    event_count: int = Field(ge=0)
    graph_rebuilt: bool = False
    detail: str = ""


class EventStoreHydrator:
    def __init__(
        self,
        repository: InvestigationRepository,
        graph_engine: ThreatGraphEngine | None = None,
    ) -> None:
        self._repository = repository
        self._graph_engine = graph_engine

    async def hydrate_investigation(self, investigation_id: str) -> HydrationReport:
        events = await self._repository.list_events(investigation_id)
        context = await self._repository.load_context(investigation_id)
        graph_rebuilt = False
        if context is not None and self._graph_engine is not None:
            await self._graph_engine.project(context)
            graph_rebuilt = True
        return HydrationReport(
            investigation_id=investigation_id,
            event_count=len(events),
            graph_rebuilt=graph_rebuilt,
            detail="hydrated from append-only event store",
        )

