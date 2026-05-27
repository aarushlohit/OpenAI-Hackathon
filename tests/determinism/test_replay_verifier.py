import unittest
from uuid import uuid4

from app.events.models import EventEnvelope, EventName
from app.memory.investigation_repository import InMemoryInvestigationRepository
from app.replay import ReplayDeterminismVerifier, ReplayEngine


class ReplayVerifierTests(unittest.IsolatedAsyncioTestCase):
    async def test_verifies_event_hashes(self) -> None:
        repository = InMemoryInvestigationRepository()
        event = EventEnvelope(
            event=EventName.INVESTIGATION_STARTED,
            correlation_id=uuid4(),
            payload={"investigation_id": "INV-ABCDEF12"},
        ).governed()
        await repository.append_event("INV-ABCDEF12", event)

        result = await ReplayDeterminismVerifier(ReplayEngine(repository)).verify("INV-ABCDEF12")

        self.assertTrue(result.verified)
        self.assertEqual(result.event_count, 1)

