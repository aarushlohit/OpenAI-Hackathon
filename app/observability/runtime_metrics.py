from collections import defaultdict

from pydantic import BaseModel, Field


class RuntimeMetricSnapshot(BaseModel):
    redis_publishes: int = Field(default=0, ge=0)
    redis_publish_failures: int = Field(default=0, ge=0)
    postgres_writes: int = Field(default=0, ge=0)
    replay_hydrations: int = Field(default=0, ge=0)
    websocket_reconnects: int = Field(default=0, ge=0)
    provider_failovers: int = Field(default=0, ge=0)
    latency_ms: dict[str, list[int]] = Field(default_factory=dict)


class RuntimeMetrics:
    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._latency: dict[str, list[int]] = defaultdict(list)

    def increment(self, name: str, amount: int = 1) -> None:
        self._counters[name] += amount

    def observe_latency(self, name: str, latency_ms: int) -> None:
        self._latency[name].append(max(latency_ms, 0))

    def snapshot(self) -> RuntimeMetricSnapshot:
        return RuntimeMetricSnapshot(
            redis_publishes=self._counters["redis_publishes"],
            redis_publish_failures=self._counters["redis_publish_failures"],
            postgres_writes=self._counters["postgres_writes"],
            replay_hydrations=self._counters["replay_hydrations"],
            websocket_reconnects=self._counters["websocket_reconnects"],
            provider_failovers=self._counters["provider_failovers"],
            latency_ms={key: list(value) for key, value in self._latency.items()},
        )
