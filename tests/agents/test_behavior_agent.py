import unittest

from app.agents.base import AgentContext
from app.agents.behavior import BehaviorAnalysisAgent
from app.events.bus import InMemoryEventBus
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationRequest


class BehaviorAgentTests(unittest.IsolatedAsyncioTestCase):
    async def test_detects_refundable_deposit_and_telegram(self) -> None:
        agent = BehaviorAnalysisAgent(PromptRegistry())
        request = InvestigationRequest(
            raw_input="Join Telegram now for direct offer. Pay refundable deposit today."
        )

        result = await agent.run(request, AgentContext(InMemoryEventBus()))

        self.assertIn("telegram_only_onboarding", result.detected_patterns)
        self.assertIn("refundable_deposit", result.detected_patterns)
        self.assertGreaterEqual(result.risk_score, 50)
        self.assertNotIn("definitely scam", result.explanation.lower())

