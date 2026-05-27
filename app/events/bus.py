import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import suppress
from uuid import UUID

from app.events.models import EventEnvelope


class InMemoryEventBus:
    def __init__(self, max_size: int = 500) -> None:
        self._max_size = max_size
        self._history: list[EventEnvelope] = []
        self._subscribers: set[asyncio.Queue[EventEnvelope]] = set()
        self._recorders: list[Callable[[EventEnvelope], Awaitable[None]]] = []

    async def publish(self, envelope: EventEnvelope) -> None:
        envelope = envelope.governed()
        self._history.append(envelope)
        if len(self._history) > self._max_size:
            self._history = self._history[-self._max_size :]
        for recorder in self._recorders:
            await recorder(envelope)
        for subscriber in list(self._subscribers):
            await subscriber.put(envelope)

    async def stream(self, correlation_id: UUID | None = None) -> AsyncIterator[EventEnvelope]:
        queue: asyncio.Queue[EventEnvelope] = asyncio.Queue(maxsize=self._max_size)
        for event in self.replay(correlation_id):
            await queue.put(event)
        self._subscribers.add(queue)
        try:
            while True:
                event = await queue.get()
                if correlation_id is None or event.correlation_id == correlation_id:
                    yield event
        finally:
            self._subscribers.discard(queue)

    def replay(self, correlation_id: UUID | None = None) -> list[EventEnvelope]:
        if correlation_id is None:
            return list(self._history)
        return [event for event in self._history if event.correlation_id == correlation_id]

    async def publish_many(self, envelopes: list[EventEnvelope]) -> None:
        for envelope in envelopes:
            await self.publish(envelope)

    async def close(self) -> None:
        if not self._history:
            self._subscribers.clear()
            return
        for subscriber in list(self._subscribers):
            with suppress(asyncio.QueueFull):
                subscriber.put_nowait(self._history[-1])
        self._subscribers.clear()

    def add_recorder(self, recorder: Callable[[EventEnvelope], Awaitable[None]]) -> None:
        self._recorders.append(recorder)
