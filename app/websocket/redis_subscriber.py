from collections.abc import AsyncIterator
from uuid import UUID

from app.runtime.redis_runtime import RedisRuntime
from app.websocket.event_serializer import WebsocketEventPayload


class RedisWebsocketSubscriber:
    def __init__(self, redis: RedisRuntime) -> None:
        self._redis = redis

    async def subscribe(self, correlation_id: UUID) -> AsyncIterator[WebsocketEventPayload]:
        channel = f"hermes:investigation:{correlation_id}"
        async for message in self._redis.subscribe(channel):
            yield WebsocketEventPayload.model_validate_json(message)

