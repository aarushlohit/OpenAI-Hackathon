from pydantic import BaseModel, Field

from app.memory.threat_memory import ThreatMemory


class WatchTarget(BaseModel):
    entity: str = Field(min_length=1, max_length=255)
    entity_type: str = Field(min_length=1, max_length=80)


class EntityWatcher:
    def __init__(self, threat_memory: ThreatMemory) -> None:
        self._threat_memory = threat_memory

    async def check(self, target: WatchTarget) -> list[str]:
        return await self._threat_memory.related_to(target.entity)

