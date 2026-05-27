# Hermes-X

Hermes-X is an autonomous AI-powered cyber defense platform focused on protecting students from internship and recruitment scams.

Phase 8.5 extends Hermes-X with deterministic replay snapshots, runtime health APIs, trace context, dead-letter queues, diagnostics, sandbox replay, backpressure controls, and safe failover primitives. Real provider network clients, durable database adapters, and sandboxed artifact analysis are still intentionally deferred.

## Run

```bash
python hermes.py investigate "https://example.com/internship"
```

Install dependencies first when starting from a clean environment:

```bash
python -m pip install -e ".[dev]"
```

## Structure

```text
.
├── app
│   ├── agents          # Orchestrator and autonomous investigation agents
│   ├── api             # FastAPI transport layer
│   ├── core            # Settings, dependency composition, shared errors
│   ├── events          # Event envelope and async event bus
│   ├── gateway         # AI provider routers and provider adapters
│   ├── memory          # Persistent memory contracts and local adapter
│   ├── models          # Shared domain value objects
│   ├── observability   # Provider metrics and circuit breaker state
│   ├── prompts         # Versioned prompt assets
│   ├── scoring         # Final threat scoring engine
│   ├── schemas         # Pydantic request and response contracts
│   ├── security        # Zero-trust input policies
│   ├── services        # Intelligence service abstractions
│   └── terminal        # Rich/Typer operator CLI
├── docs                # Documentation index and future long-form docs
├── prompts             # Prompt packs for gateway-aware services
├── frontend/flutter_app # Flutter presentation layer scaffold
├── frontend/browser_extension # Hermes Sentinel MV3 extension scaffold
├── hermes.py           # CLI entrypoint
├── main.py             # FastAPI ASGI entrypoint
└── *.md                # Required architecture and operator documents
```

## Architecture Guardrails

- Agents never call providers directly.
- AI access goes through text, vision, audio, and embedding routers.
- Inputs and AI outputs must be schema-validated.
- Secrets stay in environment-backed settings.
- Components communicate through structured events.
