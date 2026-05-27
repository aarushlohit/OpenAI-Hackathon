from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field

from app.contracts.schema_registry import SchemaRegistry
from app.governance.agent_registry import AgentContractRegistry
from app.runtime.redis_runtime import RedisRuntime
from app.websocket.manager import WebsocketConnectionManager


class BootstrapCheck(BaseModel):
    name: str
    status: str
    required: bool = True
    detail: str = ""


class BootstrapReport(BaseModel):
    ready: bool
    checks: list[BootstrapCheck] = Field(default_factory=list)


class RuntimeBootstrap:
    def __init__(
        self,
        schema_registry: SchemaRegistry,
        agent_contracts: AgentContractRegistry,
        websocket_manager: WebsocketConnectionManager,
        redis_runtime: RedisRuntime | None = None,
        postgres_ping: Callable[[], Awaitable[bool]] | None = None,
    ) -> None:
        self._schema_registry = schema_registry
        self._agent_contracts = agent_contracts
        self._websocket_manager = websocket_manager
        self._redis_runtime = redis_runtime
        self._postgres_ping = postgres_ping

    async def verify(self) -> BootstrapReport:
        checks = [
            BootstrapCheck(name="schema_registry", status="ok"),
            BootstrapCheck(name="governance_registry", status=self._governance_status()),
            BootstrapCheck(name="websocket_runtime", status=self._websocket_status()),
        ]
        if self._postgres_ping is not None:
            checks.append(await self._check_postgres())
        if self._redis_runtime is not None:
            checks.append(await self._check_redis())
        ready = all(check.status == "ok" or not check.required for check in checks)
        return BootstrapReport(ready=ready, checks=checks)

    def _governance_status(self) -> str:
        return "ok" if self._agent_contracts.get("intake") is not None else "degraded"

    def _websocket_status(self) -> str:
        return "ok" if self._websocket_manager is not None else "degraded"

    async def _check_postgres(self) -> BootstrapCheck:
        try:
            reachable = await self._postgres_ping()
        except Exception as exc:
            return BootstrapCheck(name="postgres", status="degraded", detail=str(exc))
        return BootstrapCheck(name="postgres", status="ok" if reachable else "degraded")

    async def _check_redis(self) -> BootstrapCheck:
        status = await self._redis_runtime.ping()
        return BootstrapCheck(
            name="redis",
            status="ok" if status.reachable else "degraded",
            detail=status.detail,
        )

