import unittest
from uuid import uuid4

from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName


class EventBusLoadTests(unittest.IsolatedAsyncioTestCase):
    async def test_retains_bounded_history_for_many_events(self) -> None:
        bus = InMemoryEventBus(max_size=10)
        for _ in range(100):
            await bus.publish(EventEnvelope(event=EventName.THREAT_FEED_UPDATE, correlation_id=uuid4()))

        self.assertEqual(len(bus.replay()), 10)

