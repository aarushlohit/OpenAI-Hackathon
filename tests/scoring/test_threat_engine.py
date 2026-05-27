import unittest

from app.models.behavior_result import BehaviorResult
from app.scoring import ThreatScoringEngine


class ThreatEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_scores_high_risk_behavior(self) -> None:
        score = await ThreatScoringEngine().score(
            "INV-ABCDEF12",
            [
                BehaviorResult(
                    investigation_id="INV-ABCDEF12",
                    risk_score=90,
                    confidence=0.9,
                    detected_patterns=["payment_coercion", "telegram_only_onboarding"],
                    explanation="Detected high-risk social engineering patterns.",
                )
            ],
        )

        self.assertGreaterEqual(score.final_score, 35)
        self.assertIn("payment_coercion", score.contributing_factors)

