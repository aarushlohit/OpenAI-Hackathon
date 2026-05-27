from collections.abc import AsyncIterator
import asyncio
from typing import Any

from pydantic import BaseModel, Field


class RedisRuntimeStatus(BaseModel):
    reachable: bool
    subscriber_count: int = Field(default=0, ge=0)
    detail: str = ""


class RedisRuntime:
    def __init__(self, client: Any | None = None) -> None:
        self._client = client

    async def ping(self) -> RedisRuntimeStatus:
        if self._client is None:
            return RedisRuntimeStatus(reachable=False, detail="Redis client is not configured")
        try:
            await asyncio.wait_for(self._client.ping(), timeout=2)
        except Exception as exc:
            return RedisRuntimeStatus(reachable=False, detail=str(exc))
        return RedisRuntimeStatus(reachable=True)

    async def publish(self, channel: str, payload: str) -> int:
        self._require_safe_channel(channel)
        if self._client is None:
            return 0
        published = await self._client.publish(channel, payload)
        return int(published or 0)

    async def close(self) -> None:
        if self._client is None:
            return
        close = getattr(self._client, "aclose", None) or getattr(self._client, "close", None)
        if close is not None:
            result = close()
            if hasattr(result, "__await__"):
                await result

    async def subscribe(self, channel: str) -> AsyncIterator[str]:
        self._require_safe_channel(channel)
        if self._client is None:
            return
        pubsub = self._client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                data = message.get("data", "")
                yield data.decode("utf-8") if isinstance(data, bytes) else str(data)
        finally:
            await pubsub.unsubscribe(channel)
            close = getattr(pubsub, "close", None)
            if close is not None:
                await close()

    def _require_safe_channel(self, channel: str) -> None:
        if not channel.startswith("hermes:"):
            raise ValueError("Redis channels must use the hermes namespace")
        if any(character.isspace() for character in channel):
            raise ValueError("Redis channels may not contain whitespace")
