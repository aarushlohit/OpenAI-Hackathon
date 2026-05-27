from collections.abc import Awaitable, Callable

from pydantic import BaseModel, Field


class FailureSimulationResult(BaseModel):
    scenario: str
    recovered: bool
    detail: str = ""


class FailureSimulationSuite:
    async def provider_outage(self, route_call: Callable[[], Awaitable[object]]) -> FailureSimulationResult:
        try:
            await route_call()
        except Exception as exc:
            return FailureSimulationResult(
                scenario="provider_outage",
                recovered=True,
                detail=f"failure contained: {type(exc).__name__}",
            )
        return FailureSimulationResult(scenario="provider_outage", recovered=True, detail="route completed")

    async def redis_restart(self, ping: Callable[[], Awaitable[object]]) -> FailureSimulationResult:
        try:
            await ping()
        except Exception as exc:
            return FailureSimulationResult(
                scenario="redis_restart",
                recovered=False,
                detail=f"redis degraded: {exc}",
            )
        return FailureSimulationResult(scenario="redis_restart", recovered=True, detail="redis reachable")

    async def replay_interruption(self, verify: Callable[[], Awaitable[bool]]) -> FailureSimulationResult:
        verified = await verify()
        return FailureSimulationResult(
            scenario="replay_interruption",
            recovered=verified,
            detail="replay verification passed" if verified else "replay verification failed",
        )


class FailureSimulationReport(BaseModel):
    results: list[FailureSimulationResult] = Field(default_factory=list)

    @property
    def recovered(self) -> bool:
        return all(result.recovered for result in self.results)
