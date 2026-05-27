import unittest

from app.graph.projections import ThreatGraphNode, ThreatGraphProjection, ThreatNodeKind
from app.intelligence import CampaignDetector, ThreatCorrelationEngine
from app.graph.repositories import InMemoryGraphRepository


class CampaignDetectorTests(unittest.IsolatedAsyncioTestCase):
    async def test_detects_reused_payment_method(self) -> None:
        repository = InMemoryGraphRepository()
        for investigation_id in ["INV-ABCDEF12", "INV-123456AB"]:
            await repository.save_projection(
                ThreatGraphProjection(
                    investigation_id=investigation_id,
                    nodes=[
                        ThreatGraphNode(id=investigation_id, label=investigation_id, kind=ThreatNodeKind.INVESTIGATION),
                        ThreatGraphNode(id="pay@upi", label="pay@upi", kind=ThreatNodeKind.UPI),
                    ],
                )
            )

        projection = await repository.get_projection("INV-ABCDEF12")
        summary = await ThreatCorrelationEngine(repository, CampaignDetector()).correlate(projection)

        self.assertTrue(summary.campaign_detections)
        self.assertIn("INV-123456AB", summary.related_investigations)

