import asyncio
from collections.abc import AsyncIterator
from uuid import UUID

from app.events.bus import InMemoryEventBus
from app.websocket.event_serializer import EventSerializer
from app.websocket.subscriptions import SubscriptionRegistry


class WebsocketConnectionManager:
    def __init__(self, event_bus: InMemoryEventBus, serializer: EventSerializer | None = None) -> None:
        self._event_bus = event_bus
        self._serializer = serializer or EventSerializer()
        self._subscriptions = SubscriptionRegistry()
        self._max_messages_per_subscription = 1_000

    async def subscribe(self, correlation_id: UUID, replay: bool = True) -> AsyncIterator[str]:
        subscription = self._subscriptions.create(correlation_id, replay)
        try:
            if replay:
                for event in self._event_bus.replay(correlation_id):
                    yield self._serializer.serialize(event)
            count = 0
            async for event in self._event_bus.stream(correlation_id=correlation_id):
                if self._subscriptions.accepts(subscription, event):
                    yield self._serializer.serialize(event)
                    count += 1
                    if count >= self._max_messages_per_subscription:
                        return
                    await asyncio.sleep(0)
        finally:
            self._subscriptions.remove(subscription.subscription_id)
