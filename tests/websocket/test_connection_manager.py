import json
import unittest
from uuid import uuid4

from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName
from app.websocket.manager import WebsocketConnectionManager


class WebsocketConnectionManagerTests(unittest.IsolatedAsyncioTestCase):
    async def test_replay_delivers_existing_events_to_new_subscriber(self) -> None:
        correlation_id = uuid4()
        bus = InMemoryEventBus()
        await bus.publish(
            EventEnvelope(
                event=EventName.INVESTIGATION_STARTED,
                correlation_id=correlation_id,
                payload={"investigation_id": "INV-ABCDEF12"},
            )
        )

        stream = WebsocketConnectionManager(bus).subscribe(correlation_id, replay=True)
        payload = json.loads(await anext(stream))

        self.assertEqual(payload["event"], "investigation_started")

