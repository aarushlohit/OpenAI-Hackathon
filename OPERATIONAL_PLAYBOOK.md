# Operational Playbook

Local activation:

```bash
docker compose up --build
```

MVP launcher:

```bash
./scripts/start_hermes.sh
```

Runtime validation:

```bash
python scripts/final_runtime_validation.py --json
```

Strict validation:

```bash
python scripts/final_runtime_validation.py --strict
```

CLI investigation:

```bash
python hermes.py investigate "Join Telegram @fakehr and pay refundable deposit to pay@upi"
```

Demo presets:

```bash
./scripts/demo_mode.sh telegram_onboarding_scam
./scripts/demo_mode.sh fake_internship_portal
./scripts/demo_mode.sh forged_offer_letter
./scripts/demo_mode.sh recruiter_impersonation
./scripts/demo_mode.sh coordinated_campaign
```

Operational checks:

- `/v1/runtime/health`
- `/v1/runtime/readiness`
- `/v1/runtime/bootstrap`
- `/v1/observability/runtime-metrics`
- `/v1/providers/capabilities`

Failure rule:

If Redis is down, realtime fanout degrades. If PostgreSQL is down in production, readiness must fail. Historical events are never rewritten to recover state.
