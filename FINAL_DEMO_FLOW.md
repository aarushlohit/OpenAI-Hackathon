# Final Demo Flow

Judge-ready scenarios:

1. Telegram onboarding scam.
2. Phishing portal analysis.
3. Forged offer letter analysis.
4. Coordinated campaign replay.

Expected runtime sequence:

1. Operator starts an investigation from CLI or API.
2. Intake validates untrusted input.
3. Orchestrator selects workflow.
4. Agents emit lifecycle and progress events.
5. Graph projection emits entity relationships.
6. Threat engine produces explainable severity.
7. Replay session reconstructs the timeline.
8. Story builder creates an executive narrative.
9. Websocket clients render the live command-center view.

Demo mode uses normal events and replay-safe frames. It does not patch production verdicts.

MVP demo command:

```bash
./scripts/demo_mode.sh telegram_onboarding_scam
```

Final cinematic scenario:

```text
Telegram recruiter asks for refundable onboarding payment, provides UPI pay@upi,
uses @careerfastjob, and links career-fasttrack-placement.xyz.
```

Expected:

- urgency and scarcity detection.
- graph node growth for domain, Telegram handle, and UPI.
- payment-method relationship edge.
- HIGH RISK verdict.
- replay reconstruction.
