# Investigation Lifecycle

The lifecycle is event-native and replay-safe.

1. `investigation_started`: workflow selected and investigation context created.
2. `investigation_progress`: orchestrator progress, warnings, and risk-profile stages.
3. `agent_started`: an agent begins work.
4. `agent_progress`: an agent emits explainable progress.
5. `agent_completed`: an agent completed and duration was recorded.
6. `agent_failed`: an agent failed, timed out, or was unavailable; investigation continues with partial evidence.
7. `threat_detected`: high or critical risk threshold was reached.
8. `investigation_completed`: final finding and threat score were emitted.
9. `investigation_replay`: replay projection for historical review.

Every event includes UUID correlation and an operator-facing `INV-XXXXXXXX` identifier in payload.

