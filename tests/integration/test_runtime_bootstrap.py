import unittest

from app.contracts.schema_registry import SchemaRegistry
from app.events.bus import InMemoryEventBus
from app.governance.agent_registry import AgentContractRegistry
from app.governance.permissions import AgentPermissions
from app.runtime.bootstrap import RuntimeBootstrap
from app.runtime.redis_runtime import RedisRuntime
from app.websocket.manager import WebsocketConnectionManager


class RuntimeBootstrapTests(unittest.IsolatedAsyncioTestCase):
    async def test_bootstrap_reports_ready_with_core_registries(self) -> None:
        contracts = AgentContractRegistry()
        contracts.register(
            "intake",
            AgentPermissions(
                emits=["agent_progress"],
                workflows=["url_intelligence"],
                actions=["validate_input"],
                confidence_limit=1.0,
            ),
        )
        bootstrap = RuntimeBootstrap(
            schema_registry=SchemaRegistry(),
            agent_contracts=contracts,
            websocket_manager=WebsocketConnectionManager(InMemoryEventBus()),
            redis_runtime=RedisRuntime(),
        )

        report = await bootstrap.verify()

        self.assertFalse(report.ready)
        self.assertEqual(report.checks[0].status, "ok")
        self.assertTrue(any(check.name == "redis" for check in report.checks))


if __name__ == "__main__":
    unittest.main()

