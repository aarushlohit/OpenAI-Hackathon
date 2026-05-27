import unittest

from app.diagnostics import ReplayAnalyzer
from app.replay.replay_engine import ReplaySession


class ReplayAnalyzerTests(unittest.TestCase):
    def test_empty_session_is_ordered(self) -> None:
        result = ReplayAnalyzer().analyze(ReplaySession(investigation_id="INV-ABCDEF12"))

        self.assertTrue(result["ordered"])

