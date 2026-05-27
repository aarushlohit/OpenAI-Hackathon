from app.governance.agent_registry import AgentContractRegistry


class ContractValidator:
    def __init__(self, registry: AgentContractRegistry) -> None:
        self._registry = registry

    def validate_required_agents(self, agents: list[str]) -> bool:
        return all(self._registry.get(agent) is not None for agent in agents)

