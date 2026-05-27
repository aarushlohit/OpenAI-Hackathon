from pydantic import BaseModel, Field


class HealthCheckResult(BaseModel):
    name: str
    status: str
    detail: str = ""
    latency_ms: int = Field(default=0, ge=0)


class RuntimeHealthChecks:
    async def check_websocket(self, subscriber_count: int) -> HealthCheckResult:
        status = "ok" if subscriber_count >= 0 else "degraded"
        return HealthCheckResult(name="websocket", status=status)

    async def check_replay(self, last_latency_ms: int = 0) -> HealthCheckResult:
        status = "ok" if last_latency_ms < 2_000 else "degraded"
        return HealthCheckResult(name="replay", status=status, latency_ms=last_latency_ms)

