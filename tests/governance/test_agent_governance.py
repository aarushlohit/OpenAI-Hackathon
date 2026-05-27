import unittest
from pathlib import Path

from app.governance import AgentContractRegistry, GovernancePolicy


class AgentGovernanceTests(unittest.TestCase):
    def test_contract_allows_registered_event(self) -> None:
        registry = AgentContractRegistry()
        registry.load_yaml(Path("AGENT_CONTRACT.yaml"))
        decision = GovernancePolicy(registry).can_emit("behavior", "agent_progress")

        self.assertTrue(decision.allowed)

    def test_contract_rejects_unregistered_event(self) -> None:
        registry = AgentContractRegistry()
        registry.load_yaml(Path("AGENT_CONTRACT.yaml"))
        decision = GovernancePolicy(registry).can_emit("behavior", "campaign_detected")

        self.assertFalse(decision.allowed)

