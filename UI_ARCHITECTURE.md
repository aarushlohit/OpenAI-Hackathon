# UI Architecture

The Hermes-X frontend is a presentation layer only.

Responsibilities:

- Render websocket events.
- Display investigation timelines.
- Show threat severity, provider status, and agent activity.
- Visualize graph projections.
- Render realtime graph node, edge, campaign, and entity correlation events.
- Support replay and export views.
- Render SOC operations panels such as live threat feed, campaign status, and provider infrastructure.

Non-responsibilities:

- No orchestration logic.
- No provider logic.
- No threat scoring.
- No decision-making.

Flutter structure:

- `core/websocket`: websocket transport.
- `models`: immutable event and graph contracts.
- `investigation`: repository abstraction.
- `timeline`: chronological event rendering.
- `dashboard`: SOC-style investigation screen.
- `graph`: graph projection rendering foundation.
- `widgets`: reusable visual primitives.
- `theme`: professional cyber intelligence theme.

Phase 7 panels:

- Threat feed panel.
- Active campaign panel.
- Provider status panel.
- Severity meter.

Phase 10 rendering:

- Websocket events include schema version, schema hash, producer, and trace context.
- Timeline and replay views should show trace-aware event ancestry where space allows.
- Provider status should derive from backend capability and observability endpoints, not frontend inference.

Hermes Sentinel:

- Browser extension lives under `frontend/browser_extension`.
- It consumes protection APIs only.
- It must not contain threat scoring, provider access, or orchestration logic.
