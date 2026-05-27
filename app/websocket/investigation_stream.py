from collections.abc import AsyncIterator
from uuid import UUID

from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope


class InvestigationStream:
    def __init__(self, event_bus: InMemoryEventBus) -> None:
        self._event_bus = event_bus

    async def stream(self, correlation_id: UUID) -> AsyncIterator[EventEnvelope]:
        async for event in self._event_bus.stream(correlation_id=correlation_id):
            yield event
