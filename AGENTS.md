# Agent Architecture

Hermes-X agents are autonomous workers coordinated by an orchestrator. They communicate through structured events and receive only the minimum context needed for their task.

Phase 1 agents:

- `IntakeAgent`: validates untrusted operator input against zero-trust intake policy.
- `InvestigationOrchestrator`: sequences agents, publishes lifecycle events, and persists the final Phase 1 memory record.

Planned agents:

- `OSINTAgent`: collects public signals about recruiters, domains, companies, and job posts.
- `DocumentForensicsAgent`: analyzes offer letters and PDF metadata in a sandbox.
- `PhishingAgent`: inspects URLs, domains, redirects, TLS posture, and brand impersonation.
- `SocialGraphAgent`: maps recruiter impersonation and Telegram onboarding patterns.
- `RiskSynthesisAgent`: merges evidence into a validated finding.

Invariant: agents never receive API keys and never instantiate AI provider clients.

