import unittest
from uuid import uuid4

from app.autonomous import AutonomousMonitorEngine
from app.autonomous.alerting import EscalationRules
from app.autonomous.watchers import EntityWatcher, WatchTarget
from app.events.bus import InMemoryEventBus
from app.graph.projections import ThreatGraphNode, ThreatGraphProjection, ThreatNodeKind
from app.intelligence import ThreatFeed
from app.memory.entity_index import EntityIndex
from app.memory.threat_memory import ThreatMemory


class MonitorEngineTests(unittest.IsolatedAsyncioTestCase):
    async def test_monitor_emits_threat_feed_for_known_entity(self) -> None:
        bus = InMemoryEventBus()
        memory = ThreatMemory(EntityIndex())
        await memory.remember(
            ThreatGraphProjection(
                investigation_id="INV-ABCDEF12",
                nodes=[
                    ThreatGraphNode(id="INV-ABCDEF12", label="INV-ABCDEF12", kind=ThreatNodeKind.INVESTIGATION),
                    ThreatGraphNode(id="pay@upi", label="pay@upi", kind=ThreatNodeKind.UPI),
                ],
            )
        )
        feed = ThreatFeed()
        engine = AutonomousMonitorEngine(EntityWatcher(memory), EscalationRules(), bus, feed)

        await engine.monitor(WatchTarget(entity="pay@upi", entity_type="upi"))

        self.assertEqual(len(await feed.latest()), 1)
        self.assertTrue(bus.replay())

