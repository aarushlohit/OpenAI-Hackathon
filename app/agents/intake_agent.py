from app.agents.base import AgentContext, InvestigationAgent
from app.schemas.investigation import InvestigationRequest
from app.security.input_policy import IntakePolicy


class IntakeAgent(InvestigationAgent):
    name = "intake"

    def __init__(self, policy: IntakePolicy) -> None:
        self._policy = policy

    async def run(self, request: InvestigationRequest, context: AgentContext) -> None:
        await context.log(request, self.name, "Validating untrusted investigation input")
        self._policy.validate(request)
        await context.log(request, self.name, "Input accepted for controlled analysis")
