import unittest
from uuid import uuid4

from app.database.postgres.event_store import PostgresEventStore
from app.events.models import EventEnvelope, EventName


class FakeRunner:
    def __init__(self) -> None:
        self.calls = []
        self.rows = []

    async def execute(self, statement, parameters=None):
        self.calls.append((statement, parameters or {}))
        return self.rows


class PostgresEventStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_append_uses_append_only_event_log(self) -> None:
        runner = FakeRunner()
        store = PostgresEventStore(runner)
        event = EventEnvelope(
            event=EventName.INVESTIGATION_STARTED,
            correlation_id=uuid4(),
            payload={"investigation_id": "INV-ABCDEF12"},
        )

        result = await store.append("INV-ABCDEF12", event)

        statement, params = runner.calls[0]
        self.assertIn("INSERT INTO event_log", statement)
        self.assertIn("ON CONFLICT (event_id) DO NOTHING", statement)
        self.assertEqual(params["investigation_id"], "INV-ABCDEF12")
        self.assertTrue(params["schema_hash"])
        self.assertEqual(result.investigation_id, "INV-ABCDEF12")

    async def test_list_reconstructs_envelopes_in_order_query(self) -> None:
        runner = FakeRunner()
        event = EventEnvelope(
            event=EventName.AGENT_STARTED,
            correlation_id=uuid4(),
            agent="behavior",
            payload={"investigation_id": "INV-ABCDEF12"},
        ).governed()
        runner.rows = [{"payload": event.model_dump_json()}]
        store = PostgresEventStore(runner)

        events = await store.list_for_investigation("INV-ABCDEF12")

        self.assertEqual(events[0].event, EventName.AGENT_STARTED)
        self.assertIn("ORDER BY occurred_at ASC, sequence_id ASC", runner.calls[0][0])


if __name__ == "__main__":
    unittest.main()

