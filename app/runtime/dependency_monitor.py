from pydantic import BaseModel, Field


class DependencyStatus(BaseModel):
    name: str
    status: str
    required: bool = True
    detail: str = ""


class DependencyMonitor:
    def snapshot(self) -> list[DependencyStatus]:
        return [
            DependencyStatus(name="redis", status="configured"),
            DependencyStatus(name="postgres", status="configured"),
            DependencyStatus(name="neo4j", status="optional", required=False),
        ]

