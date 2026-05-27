# Dead-Letter Queues

Dead-letter queues quarantine malformed or unauthorized events.

Captured cases:

- malformed events.
- failed projections.
- replay corruption.
- invalid schemas.
- unauthorized events.

Dead-letter records are replay-safe audit artifacts and include reason, optional event, diagnostic text, and quarantine timestamp.

