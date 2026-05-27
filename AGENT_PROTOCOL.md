# Agent Protocol

Hermes-X agents are modular intelligence workers coordinated by the orchestrator.

Rules:

- Agents have one responsibility.
- Agents receive typed `InvestigationRequest` input.
- Agents return typed result contracts.
- Agents emit progress through `AgentContext`.
- Agents never call providers directly.
- Agents never implement retry, failover, or circuit breaker behavior.
- Agents never write directly to databases.

Lifecycle:

1. `agent_started`
2. `agent_progress`
3. `agent_completed`
4. Optional `threat_detected`
5. `investigation_completed`

Phase 3 agents:

- `BehaviorAnalysisAgent`: detects social engineering patterns.
- `OSINTAgent`: correlates domain, reputation, and scam indicators.
- `VisionAnalysisAgent`: performs OCR-first visual artifact analysis.

