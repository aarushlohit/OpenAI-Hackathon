import unittest

from app.gateway.failover_controls import FailoverControls


class FailoverControlsTests(unittest.TestCase):
    def test_locked_provider_is_unavailable(self) -> None:
        controls = FailoverControls()
        controls.lock("openai")

        self.assertFalse(controls.available("openai"))

