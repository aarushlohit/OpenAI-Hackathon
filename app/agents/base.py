from abc import ABC, abstractmethod

from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName
from app.schemas.investigation import InvestigationRequest
from app.contracts.agent_result import AgentResult


class AgentContext:
    def __init__(self, event_bus: InMemoryEventBus) -> None:
        self.event_bus = event_bus

    async def log(self, request: InvestigationRequest, agent: str, message: str) -> None:
        await self.event_bus.publish(
            EventEnvelope(
                event=EventName.AGENT_PROGRESS,
                correlation_id=request.correlation_id,
                agent=agent,
                payload={"investigation_id": request.investigation_id, "message": message},
            )
        )


class InvestigationAgent(ABC):
    name: str

    @abstractmethod
    async def run(self, request: InvestigationRequest, context: AgentContext) -> AgentResult | None:
        raise NotImplementedError
