import unittest

from app.agents.base import AgentContext
from app.agents.behavior import BehaviorAnalysisAgent
from app.events.bus import InMemoryEventBus
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationRequest


class BehaviorAgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_fails_closed_without_provider(self) -> None:
        agent = BehaviorAnalysisAgent(PromptRegistry())
        request = InvestigationRequest(
            raw_input="Join Telegram now for direct offer. Pay refundable deposit today."
        )

        with self.assertRaisesRegex(RuntimeError, "NVIDIA runtime unavailable"):
            await agent.run(request, AgentContext(InMemoryEventBus()))
