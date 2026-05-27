from datetime import UTC, datetime, timedelta
from enum import StrEnum


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_seconds: int = 60) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_window = timedelta(seconds=recovery_seconds)
        self._failures: dict[str, int] = {}
        self._opened_at: dict[str, datetime] = {}

    def state_for(self, provider: str) -> CircuitState:
        opened_at = self._opened_at.get(provider)
        if opened_at is None:
            return CircuitState.CLOSED
        if datetime.now(UTC) - opened_at >= self._recovery_window:
            return CircuitState.HALF_OPEN
        return CircuitState.OPEN

    def allow_request(self, provider: str) -> bool:
        return self.state_for(provider) != CircuitState.OPEN

    def record_success(self, provider: str) -> None:
        self._failures.pop(provider, None)
        self._opened_at.pop(provider, None)

    def record_failure(self, provider: str) -> None:
        failures = self._failures.get(provider, 0) + 1
        self._failures[provider] = failures
        if failures >= self._failure_threshold:
            self._opened_at[provider] = datetime.now(UTC)

