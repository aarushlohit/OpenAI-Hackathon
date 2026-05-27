import unittest
from uuid import uuid4

from app.models.investigation_context import InvestigationContext, InvestigationEntities
from app.models.threat_score import ThreatScore, ThreatSeverity
from app.reporting import StoryBuilder


class StoryBuilderTests(unittest.TestCase):
    def test_builds_evidence_narrative(self) -> None:
        context = InvestigationContext(
            investigation_id="INV-ABCDEF12",
            correlation_id=uuid4(),
            raw_input="signal",
            evidence_kind="text",
            entities=InvestigationEntities(domains=["fake.example"], upi_ids=["pay@upi"]),
        )
        score = ThreatScore(
            investigation_id="INV-ABCDEF12",
            final_score=80,
            severity=ThreatSeverity.HIGH,
            explanation="High risk evidence.",
            contributing_factors=["payment_coercion"],
        )

        narrative = StoryBuilder().build(context, score)

        self.assertIn("fake.example", " ".join(narrative.key_points))

