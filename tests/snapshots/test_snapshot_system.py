import unittest
from uuid import uuid4

from app.events.models import EventEnvelope, EventName
from app.replay.replay_engine import ReplaySession, ReplayFrame
from app.replay.snapshot_builder import SnapshotBuilder
from app.replay.snapshot_validator import SnapshotValidator


class SnapshotSystemTests(unittest.TestCase):
    def test_snapshot_is_deterministic(self) -> None:
        event = EventEnvelope(event=EventName.INVESTIGATION_STARTED, correlation_id=uuid4()).governed()
        session = ReplaySession(
            investigation_id="INV-ABCDEF12",
            frames=[ReplayFrame(index=0, event=event, offset_ms=0, integrity_hash="hash")],
        )
        builder = SnapshotBuilder()

        self.assertTrue(SnapshotValidator().validate(builder.build(session), builder.build(session)))

