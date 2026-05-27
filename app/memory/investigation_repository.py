from abc import ABC, abstractmethod

from app.events.models import EventEnvelope
from app.models.investigation_context import InvestigationContext
from app.models.threat_score import ThreatScore


class InvestigationRepository(ABC):
    @abstractmethod
    async def save_context(self, context: InvestigationContext) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_context(self, investigation_id: str) -> InvestigationContext | None:
        raise NotImplementedError

    @abstractmethod
    async def append_event(self, investigation_id: str, event: EventEnvelope) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_events(self, investigation_id: str) -> list[EventEnvelope]:
        raise NotImplementedError

    @abstractmethod
    async def save_verdict(self, investigation_id: str, verdict: ThreatScore) -> None:
        raise NotImplementedError


class InMemoryInvestigationRepository(InvestigationRepository):
    def __init__(self) -> None:
        self._contexts: dict[str, InvestigationContext] = {}
        self._events: dict[str, list[EventEnvelope]] = {}
        self._verdicts: dict[str, ThreatScore] = {}

    async def save_context(self, context: InvestigationContext) -> None:
        self._contexts[context.investigation_id] = context

    async def load_context(self, investigation_id: str) -> InvestigationContext | None:
        return self._contexts.get(investigation_id)

    async def append_event(self, investigation_id: str, event: EventEnvelope) -> None:
        self._events.setdefault(investigation_id, []).append(event)

    async def list_events(self, investigation_id: str) -> list[EventEnvelope]:
        return list(self._events.get(investigation_id, []))

    async def save_verdict(self, investigation_id: str, verdict: ThreatScore) -> None:
        self._verdicts[investigation_id] = verdict

