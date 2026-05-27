import json
import unittest
from uuid import uuid4

from app.events.models import EventEnvelope, EventName
from app.websocket.event_serializer import EventSerializer


class EventSerializerTests(unittest.TestCase):
    def test_serializes_schema_valid_payload(self) -> None:
        event = EventEnvelope(
            event=EventName.AGENT_PROGRESS,
            correlation_id=uuid4(),
            agent="behavior",
            payload={"investigation_id": "INV-ABCDEF12", "message": "ok"},
        )

        raw = EventSerializer().serialize(event)
        payload = json.loads(raw)

        self.assertEqual(payload["event"], "agent_progress")
        self.assertEqual(payload["agent"], "behavior")

    def test_rejects_malformed_payload(self) -> None:
        with self.assertRaises(ValueError):
            EventSerializer().deserialize("{bad json")

