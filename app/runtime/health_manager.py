from pydantic import BaseModel, Field

from app.runtime.dependency_monitor import DependencyMonitor, DependencyStatus
from app.runtime.health_checks import HealthCheckResult, RuntimeHealthChecks


class RuntimeHealth(BaseModel):
    status: str
    checks: list[HealthCheckResult] = Field(default_factory=list)


class RuntimeHealthManager:
    def __init__(
        self,
        checks: RuntimeHealthChecks | None = None,
        dependencies: DependencyMonitor | None = None,
    ) -> None:
        self._checks = checks or RuntimeHealthChecks()
        self._dependencies = dependencies or DependencyMonitor()

    async def health(self) -> RuntimeHealth:
        checks = [await self._checks.check_websocket(0), await self._checks.check_replay()]
        status = "ok" if all(check.status == "ok" for check in checks) else "degraded"
        return RuntimeHealth(status=status, checks=checks)

    async def readiness(self) -> RuntimeHealth:
        return await self.health()

    async def liveness(self) -> RuntimeHealth:
        return RuntimeHealth(status="ok")

    def dependencies(self) -> list[DependencyStatus]:
        return self._dependencies.snapshot()

