from typing import Any


def create_redis_client(dsn: str) -> Any | None:
    try:
        from redis.asyncio import Redis
    except ImportError:
        return None
    return Redis.from_url(dsn, decode_responses=False)
