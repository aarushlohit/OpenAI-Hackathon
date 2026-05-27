import unittest
from uuid import uuid4

from app.graph import ThreatGraphEngine
from app.graph.repositories import InMemoryGraphRepository
from app.models.investigation_context import InvestigationContext, InvestigationEntities


class GraphEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_projects_context_entities(self) -> None:
        repository = InMemoryGraphRepository()
        context = InvestigationContext(
            investigation_id="INV-ABCDEF12",
            correlation_id=uuid4(),
            raw_input="signal",
            evidence_kind="text",
            entities=InvestigationEntities(domains=["fake.example"], upi_ids=["pay@upi"]),
        )

        projection = await ThreatGraphEngine(repository).project(context)

        self.assertEqual(len(projection.nodes), 3)
        self.assertEqual(len(projection.edges), 2)
        self.assertIsNotNone(await repository.get_projection("INV-ABCDEF12"))

