from datetime import timedelta

from pydantic import BaseModel, Field


class RetentionPolicy(BaseModel):
    event_days: int = Field(default=90, ge=1)
    replay_snapshot_days: int = Field(default=180, ge=1)

    def event_ttl(self) -> timedelta:
        return timedelta(days=self.event_days)

