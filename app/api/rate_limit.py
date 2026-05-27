from time import monotonic


class InMemoryRateLimiter:
    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self._limit = limit
        self._window = window_seconds
        self._hits: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = monotonic()
        hits = [hit for hit in self._hits.get(key, []) if now - hit <= self._window]
        if len(hits) >= self._limit:
            self._hits[key] = hits
            return False
        hits.append(now)
        self._hits[key] = hits
        return True

