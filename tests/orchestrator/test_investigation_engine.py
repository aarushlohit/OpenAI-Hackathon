import unittest

from app.agents.base import AgentContext, InvestigationAgent
from app.core.container import AppContainer
from app.schemas.investigation import InvestigationRequest


class FailingAgent(InvestigationAgent):
    name = "vision"

    async def run(self, request: InvestigationRequest, context: AgentContext):
        raise RuntimeError("boom")


class InvestigationEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_agent_failure_aborts_investigation(self) -> None:
        container = AppContainer()
        container.orchestrator._agents["behavior"] = FailingAgent()
        request = InvestigationRequest(raw_input="Pay refundable deposit on Telegram today")

        with self.assertRaisesRegex(RuntimeError, "Investigation aborted"):
            await container.orchestrator.investigate(request)
        events = await container.investigation_repository.list_events(request.investigation_id)

        self.assertTrue(any(event.event == "agent_failed" for event in events))
