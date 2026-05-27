# Hermes Sentinel Extension

Hermes Sentinel is the browser protection layer for students.

Location:

`frontend/browser_extension/`

Capabilities:

- Manifest V3 extension scaffold.
- URL scanning through Hermes-X protection API.
- Warning overlay for elevated-risk domains.
- Message validation for extension requests.

Current endpoints consumed:

- `/v1/protection/domain/{domain}`

Security rules:

- Never trust extension messages.
- Keep intelligence backend-side.
- Render warnings only from validated API responses.
- Do not embed provider or scoring logic in the extension.

