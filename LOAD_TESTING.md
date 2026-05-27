# Load Testing

Phase 8 adds load-test foundations for event-native resilience.

Coverage:

- bounded event bus history.
- websocket subscriber isolation.
- replay storm readiness.
- graph rebuild stress test hooks.
- concurrent investigation test hooks.

Current tests validate bounded event history. Future load suites should use real async subscribers and API-level concurrency.

Phase 8.5 additions:

- websocket subscriptions cap message delivery per subscription.
- event bus history remains bounded.
- dead-letter queues are bounded.
