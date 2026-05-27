from app.models.investigation_context import InvestigationContext


class ContextSnapshotStore:
    def __init__(self) -> None:
        self._snapshots: dict[str, list[InvestigationContext]] = {}

    async def append(self, context: InvestigationContext) -> None:
        self._snapshots.setdefault(context.investigation_id, []).append(context.model_copy(deep=True))

    async def list(self, investigation_id: str) -> list[InvestigationContext]:
        return list(self._snapshots.get(investigation_id, []))

