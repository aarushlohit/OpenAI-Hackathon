from app.models.investigation_context import InvestigationContext


class SessionMemory:
    def __init__(self) -> None:
        self._active: dict[str, InvestigationContext] = {}

    async def put(self, context: InvestigationContext) -> None:
        self._active[context.investigation_id] = context

    async def get(self, investigation_id: str) -> InvestigationContext | None:
        return self._active.get(investigation_id)

    async def remove(self, investigation_id: str) -> None:
        self._active.pop(investigation_id, None)

