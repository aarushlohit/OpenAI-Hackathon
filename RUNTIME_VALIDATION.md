# Runtime Validation

Final validation script:

```bash
python scripts/final_runtime_validation.py --json
```

Checks:

- bootstrap registry status.
- websocket event streaming.
- replay determinism.
- provider capability registry.
- graph projection engine initialization.

Use `--strict` when CI or deployment should fail on degraded dependencies.
