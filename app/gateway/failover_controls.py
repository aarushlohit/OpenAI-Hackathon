from datetime import UTC, datetime, timedelta


class FailoverControls:
    def __init__(self, cooldown_seconds: int = 30) -> None:
        self._cooldown = timedelta(seconds=cooldown_seconds)
        self._cooldowns: dict[str, datetime] = {}
        self._locks: set[str] = set()

    def lock(self, provider: str) -> None:
        self._locks.add(provider)

    def unlock(self, provider: str) -> None:
        self._locks.discard(provider)

    def mark_cooldown(self, provider: str) -> None:
        self._cooldowns[provider] = datetime.now(UTC)

    def available(self, provider: str) -> bool:
        if provider in self._locks:
            return False
        started = self._cooldowns.get(provider)
        return started is None or datetime.now(UTC) - started >= self._cooldown

