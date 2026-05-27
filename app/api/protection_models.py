from pydantic import BaseModel, Field


class ProtectionLookup(BaseModel):
    entity: str = Field(min_length=1, max_length=255)
    entity_type: str = Field(min_length=1, max_length=40)
    risk: str
    related_investigations: list[str] = Field(default_factory=list)


def build_lookup(entity: str, entity_type: str, related: list[str]) -> ProtectionLookup:
    risk = "elevated" if related else "unknown"
    return ProtectionLookup(
        entity=entity,
        entity_type=entity_type,
        risk=risk,
        related_investigations=related,
    )

