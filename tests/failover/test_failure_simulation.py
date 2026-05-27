import unittest

from app.runtime.failure_simulation import FailureSimulationSuite


class FailureSimulationTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_outage_is_contained(self) -> None:
        suite = FailureSimulationSuite()

        async def failing_route():
            raise RuntimeError("provider offline")

        result = await suite.provider_outage(failing_route)

        self.assertTrue(result.recovered)
        self.assertEqual(result.scenario, "provider_outage")

    async def test_replay_interruption_reports_verification(self) -> None:
        suite = FailureSimulationSuite()

        result = await suite.replay_interruption(lambda: self._verified())

        self.assertTrue(result.recovered)

    async def _verified(self) -> bool:
        return True


if __name__ == "__main__":
    unittest.main()

