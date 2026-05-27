from app.events.models import EventEnvelope
from app.runtime.redis_runtime import RedisRuntime
from app.websocket.event_serializer import EventSerializer


class RedisEventBroadcaster:
    def __init__(self, redis: RedisRuntime, serializer: EventSerializer | None = None) -> None:
        self._redis = redis
        self._serializer = serializer or EventSerializer()

    async def publish(self, event: EventEnvelope) -> int:
        governed = event.governed()
        channel = f"hermes:investigation:{governed.correlation_id}"
        return await self._redis.publish(channel, self._serializer.serialize(governed))

