# Governance

Hermes-X governance constrains agent behavior without changing the orchestration engine.

Components:

- `AgentContractRegistry`: loads agent contracts.
- `GovernancePolicy`: validates event and workflow permissions.
- `AgentPermissions`: declares emitted events, workflows, actions, and confidence limits.
- `RiskThresholds`: central severity thresholds.

Agents must declare:

- emitted event types.
- supported workflows.
- confidence limits.
- allowed actions.

Governance validates actions before future privileged capabilities are added.

Runtime governance:

- Dead-letter queues capture unauthorized or malformed events.
- Trace context helps identify spoofing and lineage issues.
- Websocket authorization and rate limiting primitives define production boundaries.
- Runtime bootstrap validates that the schema registry, governance registry, and websocket runtime are initialized before production readiness is trusted.
