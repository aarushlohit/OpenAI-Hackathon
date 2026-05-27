# Style Guide

Hermes-X code should be boring in the best way: explicit, typed, readable, and easy to audit.

Rules:

- Keep files under 300 lines.
- Prefer small domain modules over broad utility files.
- Use Pydantic for boundary schemas.
- Use async APIs for I/O-facing services.
- Name classes by responsibility: `TextRouter`, `IntakePolicy`, `ProviderMetrics`.
- Avoid provider-specific logic outside `app/gateway/providers`.
- Avoid `helpers.py`, `utils.py`, and ambiguous catch-all modules.

Terminal style should feel like a cyber command center without sacrificing readability.

