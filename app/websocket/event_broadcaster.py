from collections.abc import AsyncIterator
from uuid import UUID

from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope
from app.websocket.event_serializer import EventSerializer


class WebsocketEventBroadcaster:
    def __init__(self, event_bus: InMemoryEventBus) -> None:
        self._event_bus = event_bus
        self._serializer = EventSerializer()

    async def subscribe_json(self, correlation_id: UUID) -> AsyncIterator[str]:
        async for event in self._event_bus.stream(correlation_id=correlation_id):
            yield self.serialize(event)

    def serialize(self, event: EventEnvelope) -> str:
        return self._serializer.serialize(event)
