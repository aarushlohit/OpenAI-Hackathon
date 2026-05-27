import unittest

from app.core.container import AppContainer
from app.runtime.runtime_validator import RuntimeValidator


class RuntimeValidatorTests(unittest.IsolatedAsyncioTestCase):
    async def test_runtime_validator_reports_core_checks(self) -> None:
        container = AppContainer()
        report = await RuntimeValidator(container).validate()
        await container.redis_runtime.close()

        names = {check.name for check in report.checks}
        self.assertIn("provider_capabilities", names)
        self.assertIn("websocket_stream", names)
        self.assertIn("replay_determinism", names)


if __name__ == "__main__":
    unittest.main()
