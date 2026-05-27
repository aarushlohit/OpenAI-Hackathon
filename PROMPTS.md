# Prompt System

Prompts are security-sensitive runtime assets.

Rules:

- Keep system prompts outside agent business logic.
- Include explicit untrusted-input boundaries in analysis prompts.
- Request structured outputs matching Pydantic schemas.
- Never ask a model to decide whether its own output is safe.
- Never include secrets, environment values, or internal credentials.

Prompt packs will live under `prompts/` and be loaded by gateway-aware services in Phase 2.

