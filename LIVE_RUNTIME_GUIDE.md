# Live Runtime Guide

## Boot

```bash
./scripts/start_hermes.sh
```

## Demo Mode

```bash
./scripts/demo_mode.sh telegram_onboarding_scam
./scripts/demo_mode.sh coordinated_campaign
```

## Runtime Validation

```bash
python scripts/final_runtime_validation.py --json
```

## Provider Validation

```bash
python scripts/validate_live_providers.py
```

The provider validator reads `.env` and `app/.env`, sends minimal health prompts, and never prints API keys.

## Reset

Preserve data:

```bash
./scripts/reset_runtime.sh
```

Remove volumes:

```bash
CONFIRM_RESET=YES ./scripts/reset_runtime.sh --volumes
```

## WebSocket Validation

Subscribe with the investigation correlation ID:

```bash
websocat ws://localhost:8000/v1/ws/investigations/{correlation_id}
```

Expected event classes:

- agent lifecycle.
- graph nodes and edges.
- threat detection.
- provider failover.
- replay and demo frames.

