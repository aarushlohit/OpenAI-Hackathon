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
        self._last_successful_provider: str | None = None
        self._last_successful_model: str | None = None

    def record(self, trace: ProviderTrace) -> None:
        key = f"{trace.operation}:{trace.provider}"
        self._calls[key] += 1
        self._latency_ms[key].append(trace.latency_ms)
        if not trace.success:
            self._failures[key] += 1
        else:
            self._last_successful_provider = trace.provider
            # Infer model from provider
            if trace.provider == "nvidia_nim":
                self._last_successful_model = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
            elif trace.provider == "openai":
                self._last_successful_model = "gpt-4.1-mini"
            elif trace.provider == "pollinations":
                self._last_successful_model = "pollinations-text"
    
    def get_active_provider(self) -> tuple[str | None, str | None]:
        return (self._last_successful_provider, self._last_successful_model)

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
