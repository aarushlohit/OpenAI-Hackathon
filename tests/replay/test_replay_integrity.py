import unittest
from uuid import uuid4

from app.events.models import EventEnvelope, EventName
from app.memory.investigation_repository import InMemoryInvestigationRepository
from app.replay import ReplayEngine


class ReplayIntegrityTests(unittest.IsolatedAsyncioTestCase):
    async def test_replay_session_verifies_hashes(self) -> None:
        repository = InMemoryInvestigationRepository()
        await repository.append_event(
            "INV-ABCDEF12",
            EventEnvelope(
                event=EventName.INVESTIGATION_STARTED,
                correlation_id=uuid4(),
                payload={"investigation_id": "INV-ABCDEF12"},
            ),
        )

        engine = ReplayEngine(repository)
        session = await engine.build("INV-ABCDEF12")

        self.assertTrue(engine.verify(session))

