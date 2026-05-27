import unittest
from uuid import uuid4

from app.models.graph_projection import GraphProjectionBuilder
from app.models.investigation_context import InvestigationContext, InvestigationEntities


class GraphProjectionTests(unittest.TestCase):
    def test_projects_entities_into_graph(self) -> None:
        context = InvestigationContext(
            investigation_id="INV-ABCDEF12",
            correlation_id=uuid4(),
            raw_input="signal",
            evidence_kind="text",
            entities=InvestigationEntities(domains=["fake.example"], telegram_handles=["fakehr"]),
        )

        projection = GraphProjectionBuilder().build(context)

        self.assertEqual(len(projection.nodes), 3)
        self.assertEqual(len(projection.edges), 2)

