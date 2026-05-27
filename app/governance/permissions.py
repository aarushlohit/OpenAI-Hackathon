from pydantic import BaseModel, Field


class AgentPermissions(BaseModel):
    emits: set[str] = Field(default_factory=set)
    workflows: set[str] = Field(default_factory=set)
    actions: set[str] = Field(default_factory=set)
    confidence_limit: float = Field(default=1.0, ge=0, le=1)

