# Codex Operating Guide

Codex works in this repository as a conservative engineering agent. Preserve clean architecture boundaries, keep files below 300 lines, and prefer small typed modules over broad helper layers.

Primary rules:

- Do not let agents call AI providers directly.
- Route text generation through `app/gateway/text_router.py`.
- Route vision analysis through `app/gateway/vision_router.py`.
- Validate every external input before analysis.
- Treat generated AI output as untrusted until Pydantic validation succeeds.
- Keep secrets in settings only; never pass raw keys into agent contexts.

Phase 1 scope is the cognitive workspace, CLI, events, memory abstractions, and provider failover skeleton.

