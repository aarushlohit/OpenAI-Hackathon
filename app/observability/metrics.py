from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderTrace:
    investigation_id: str
    request_id: str
    provider: str
    operation: str
    latency_ms: int
    success: bool
    failure_reason: str | None = None


class ProviderMetrics:
    def __init__(self) -> None:
        self._calls: dict[str, int] = defaultdict(int)
        self._failures: dict[str, int] = defaultdict(int)
        self._latency_ms: dict[str, list[int]] = defaultdict(list)

    def record(self, trace: ProviderTrace) -> None:
        key = f"{trace.operation}:{trace.provider}"
        self._calls[key] += 1
        self._latency_ms[key].append(trace.latency_ms)
        if not trace.success:
            self._failures[key] += 1

    def snapshot(self) -> dict[str, dict[str, float | int]]:
        result: dict[str, dict[str, float | int]] = {}
        for key, calls in self._calls.items():
            latencies = self._latency_ms[key]
            result[key] = {
                "calls": calls,
                "failures": self._failures[key],
                "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            }
        return result


@dataclass(frozen=True)
class AgentTrace:
    investigation_id: str
    agent: str
    latency_ms: int
    success: bool


class AgentMetrics:
    def __init__(self) -> None:
        self._calls: dict[str, int] = defaultdict(int)
        self._failures: dict[str, int] = defaultdict(int)
        self._latency_ms: dict[str, list[int]] = defaultdict(list)

    def record(self, trace: AgentTrace) -> None:
        self._calls[trace.agent] += 1
        self._latency_ms[trace.agent].append(trace.latency_ms)
        if not trace.success:
            self._failures[trace.agent] += 1

    def snapshot(self) -> dict[str, dict[str, float | int]]:
        result: dict[str, dict[str, float | int]] = {}
        for agent, calls in self._calls.items():
            latencies = self._latency_ms[agent]
            result[agent] = {
                "calls": calls,
                "failures": self._failures[agent],
                "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            }
        return result
