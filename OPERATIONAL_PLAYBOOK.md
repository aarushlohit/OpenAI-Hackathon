# Operational Playbook

Local activation:

```bash
docker compose up --build
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

Operational checks:

- `/v1/runtime/health`
- `/v1/runtime/readiness`
- `/v1/runtime/bootstrap`
- `/v1/observability/runtime-metrics`
- `/v1/providers/capabilities`

Failure rule:

If Redis is down, realtime fanout degrades. If PostgreSQL is down in production, readiness must fail. Historical events are never rewritten to recover state.

