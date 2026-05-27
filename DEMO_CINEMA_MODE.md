# Demo Cinema Mode

Demo cinema mode provides reliable event-paced scenarios for hackathon and training presentations.

Components:

- `DemoScenarioRegistry`: curated scenario definitions.
- `CinemaMode`: emits `demo_cinema_frame` events into the normal event bus.

Current scenarios:

- Telegram onboarding scam.
- Phishing portal analysis.
- Forged offer letter.
- Coordinated campaign replay.

Cinema mode must remain replay-safe and must not hardcode fake results into production investigation logic.

Phase 10 convergence:

- Demo flows should pair live investigation output with replay frames and graph updates.
- Runtime validation should be run before judging demos.
- Demo failures must degrade visibly through events instead of patching final verdicts.
