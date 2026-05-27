import unittest
from uuid import uuid4

from app.events.models import EventEnvelope, EventName
from app.memory.investigation_repository import InMemoryInvestigationRepository
from app.runtime.hydration import EventStoreHydrator


class EventStoreHydrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_hydration_reads_persisted_event_history(self) -> None:
        repository = InMemoryInvestigationRepository()
        await repository.append_event(
            "INV-ABCDEF12",
            EventEnvelope(
                event=EventName.INVESTIGATION_STARTED,
                correlation_id=uuid4(),
                payload={"investigation_id": "INV-ABCDEF12"},
            ),
        )
        hydrator = EventStoreHydrator(repository)

        report = await hydrator.hydrate_investigation("INV-ABCDEF12")

        self.assertEqual(report.event_count, 1)
        self.assertFalse(report.graph_rebuilt)


if __name__ == "__main__":
    unittest.main()

