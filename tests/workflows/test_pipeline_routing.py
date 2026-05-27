import unittest

from app.orchestrator.pipeline_router import PipelineRouter
from app.orchestrator.workflow_registry import WorkflowRegistry
from app.schemas.investigation import InvestigationInputKind, InvestigationRequest


class PipelineRoutingTests(unittest.TestCase):
    def test_url_routes_to_url_intelligence(self) -> None:
        request = InvestigationRequest(raw_input="https://example.com", kind=InvestigationInputKind.URL)

        workflow = PipelineRouter(WorkflowRegistry()).route(request)

        self.assertEqual(workflow.name, "url_intelligence")
        self.assertIn("osint", workflow.parallel_agents)

