import unittest
from uuid import uuid4

from app.events.models import EventEnvelope, EventName
from app.memory.investigation_repository import InMemoryInvestigationRepository
from app.models.investigation_context import InvestigationContext


class InvestigationRepositoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_saves_context_and_events(self) -> None:
        repository = InMemoryInvestigationRepository()
        context = InvestigationContext(
            investigation_id="INV-ABCDEF12",
            correlation_id=uuid4(),
            raw_input="hello",
            evidence_kind="text",
        )
        event = EventEnvelope(
            event=EventName.INVESTIGATION_STARTED,
            correlation_id=context.correlation_id,
            payload={"investigation_id": context.investigation_id},
        )

        await repository.save_context(context)
        await repository.append_event(context.investigation_id, event)

        self.assertEqual(await repository.load_context(context.investigation_id), context)
        self.assertEqual(len(await repository.list_events(context.investigation_id)), 1)

