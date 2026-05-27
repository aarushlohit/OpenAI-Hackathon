import unittest

from app.evaluation import BenchmarkRunner
from app.evaluation.scenario_suite import ScenarioSuite


class BenchmarkRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_runs_scenario_suite(self) -> None:
        metrics = await BenchmarkRunner().run(ScenarioSuite().scenarios())

        self.assertEqual(metrics.replay_consistency, 1.0)

