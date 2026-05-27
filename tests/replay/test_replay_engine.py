import unittest
from uuid import uuid4

from app.events.models import EventEnvelope, EventName
from app.memory.investigation_repository import InMemoryInvestigationRepository
from app.replay import ReplayEngine


class ReplayEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_replay_preserves_event_order(self) -> None:
        repository = InMemoryInvestigationRepository()
        correlation_id = uuid4()
        for event_name in [EventName.INVESTIGATION_STARTED, EventName.INVESTIGATION_COMPLETED]:
            await repository.append_event(
                "INV-ABCDEF12",
                EventEnvelope(
                    event=event_name,
                    correlation_id=correlation_id,
                    payload={"investigation_id": "INV-ABCDEF12"},
                ),
            )

        session = await ReplayEngine(repository).build("INV-ABCDEF12")

        self.assertEqual([frame.event.event for frame in session.frames], [
            EventName.INVESTIGATION_STARTED,
            EventName.INVESTIGATION_COMPLETED,
        ])

