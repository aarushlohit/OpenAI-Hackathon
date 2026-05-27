import json
import unittest
from uuid import uuid4

from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName
from app.websocket.event_broadcaster import WebsocketEventBroadcaster


class EventBroadcasterTests(unittest.IsolatedAsyncioTestCase):
    async def test_serializes_safe_event_json(self) -> None:
        correlation_id = uuid4()
        bus = InMemoryEventBus()
        event = EventEnvelope(
            event=EventName.INVESTIGATION_PROGRESS,
            correlation_id=correlation_id,
            payload={"investigation_id": "INV-ABCDEF12", "message": "ok"},
        )
        await bus.publish(event)
        stream = WebsocketEventBroadcaster(bus).subscribe_json(correlation_id)

        payload = json.loads(await anext(stream))

        self.assertEqual(payload["payload"]["message"], "ok")

