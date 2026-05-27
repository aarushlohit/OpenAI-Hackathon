# Hermes-X

Hermes-X is a realtime autonomous cyber operations platform for recruitment fraud intelligence. It investigates fake internships, recruiter impersonation, phishing portals, forged offer letters, Telegram onboarding scams, and coordinated payment campaigns.

The current runtime includes event-driven orchestration, replay-verifiable investigations, PostgreSQL event-store adapters, Redis realtime coordination, graph-native threat intelligence, multimodal provider routing, and a Flutter SOC console scaffold.

## Runtime Architecture

```text
Flutter SOC Console
   ↓ websocket + REST
FastAPI Runtime
   ↓ typed events
Hermes Orchestrator
   ↓ agents + gateway routers
Behavior / OSINT / Vision / Threat Graph
   ↓ append-only history
Replay + Snapshots + Event Store
   ↓
PostgreSQL + Redis
```

## Replay Model

```text
EventEnvelope → append-only event log → ReplayFrame → Snapshot fingerprint
Graph events → deterministic projection → graph hash → replay verification
```

PostgreSQL stores immutable truth. Redis coordinates realtime fanout. Replay reconstructs investigations without re-running agents.

## Run

```bash
python hermes.py investigate "https://example.com/internship"
```

Install dependencies first when starting from a clean environment:

```bash
python -m pip install -e ".[dev]"
```

## Quick Start

### 1. Create `.env`

```bash
cp .env.example .env
```

Add:

- `OPENAI_API_KEY`
- `NVIDIA_NIM_API_KEY`

### 2. Boot Runtime

```bash
docker compose up --build
```

MVP launcher:

```bash
./scripts/start_hermes.sh
```

### 3. Validate Runtime

```bash
python scripts/final_runtime_validation.py --json
```

### 4. Run Investigation

```bash
python hermes.py investigate "Telegram HR asking refundable onboarding fee"
```

### 5. Start Flutter UI

```bash
cd frontend/flutter_app
flutter pub get
flutter run
```

### 6. Open API Docs

http://localhost:8000/docs

### 7. Open Neo4j Optional

http://localhost:7474

## Docker Boot

```bash
cp .env.example .env
docker compose up --build
```

Expected services:

- `api`
- `postgres`
- `redis`
- optional `neo4j`

Validate the runtime:

```bash
python scripts/final_runtime_validation.py --json
```

Validate live providers:

```bash
python scripts/validate_live_providers.py
```

## Demo Investigation

```bash
python hermes.py investigate "Telegram HR from @careerfastjob claims direct internship selection. Asks refundable onboarding payment of 3500. Provides UPI pay@upi. Sends URL: https://career-fasttrack-placement.xyz. Claims limited slots."
```

Expected result: high-risk recruitment scam indicators with graph node and edge events.

## WebSocket Flow

```text
POST /v1/investigate → correlation_id
ws://localhost:8000/v1/ws/investigations/{correlation_id}
```

Rendered event types include agent lifecycle, threat detection, graph nodes, graph edges, campaign alerts, escalation events, and demo cinema frames.

## Provider Failover

Provider routing is capability-driven:

- Text: OpenAI → NVIDIA Gemma 3n → Pollinations
- Vision: OpenAI → NVIDIA Gemma 3n → Pollinations
- Audio: OpenAI → NVIDIA Gemma 3n
- Embeddings: OpenAI → Pollinations

Agents never receive provider credentials and never instantiate provider clients.

## Structure

```text
.
├── app
│   ├── agents          # Orchestrator and autonomous investigation agents
│   ├── api             # FastAPI transport layer
│   ├── core            # Settings, dependency composition, shared errors
│   ├── events          # Event envelope and async event bus
│   ├── gateway         # AI provider routers and provider adapters
│   ├── graph           # Deterministic threat graph projection
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
├── frontend/flutter_app # Flutter realtime SOC console
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
