import unittest

from app.agents.base import AgentContext, InvestigationAgent
from app.core.container import AppContainer
from app.schemas.investigation import InvestigationRequest


class FailingAgent(InvestigationAgent):
    name = "vision"

    async def run(self, request: InvestigationRequest, context: AgentContext):
        raise RuntimeError("boom")


class InvestigationEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_partial_agent_failure_still_completes(self) -> None:
        container = AppContainer()
        container.orchestrator._agents["vision"] = FailingAgent()
        request = InvestigationRequest(raw_input="Pay refundable deposit on Telegram today")

        result = await container.orchestrator.investigate(request)
        events = await container.investigation_repository.list_events(request.investigation_id)

        self.assertEqual(result.investigation_id, request.investigation_id)
        self.assertTrue(any(event.event == "agent_failed" for event in events))

