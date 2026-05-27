from pydantic import BaseModel

from app.governance.agent_registry import AgentContractRegistry


class GovernanceDecision(BaseModel):
    allowed: bool
    reason: str


class GovernancePolicy:
    def __init__(self, registry: AgentContractRegistry) -> None:
        self._registry = registry

    def can_emit(self, agent: str, event: str) -> GovernanceDecision:
        permissions = self._registry.get(agent)
        if permissions is None:
            return GovernanceDecision(allowed=False, reason="agent_not_registered")
        if event not in permissions.emits:
            return GovernanceDecision(allowed=False, reason="event_not_permitted")
        return GovernanceDecision(allowed=True, reason="allowed")

    def eligible_for_workflow(self, agent: str, workflow: str) -> GovernanceDecision:
        permissions = self._registry.get(agent)
        if permissions is None:
            return GovernanceDecision(allowed=False, reason="agent_not_registered")
        if workflow not in permissions.workflows:
            return GovernanceDecision(allowed=False, reason="workflow_not_permitted")
        return GovernanceDecision(allowed=True, reason="allowed")

