# Hermes-X

> **Autonomous Cyber Investigation Runtime** — recruitment fraud intelligence at SOC-grade speed.

Hermes-X investigates fake internships, recruiter impersonation, phishing portals, forged offer letters, Telegram onboarding scams, and coordinated payment campaigns using a fully autonomous, event-sourced pipeline.

---

## System Doctrine

```
Events define reality.
Replay reconstructs cognition.
Graphs project intelligence.
Evidence drives escalation.
Providers reason within governed runtime boundaries.
PostgreSQL stores immutable truth.
Redis coordinates realtime cognition.
The runtime—not the model—is the system.
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Flutter SOC Dashboard                        │
│  Severity Meter │ Story Timeline │ Explainability Panel         │
│  Threat Graph   │ Replay Console │ Observability Panel          │
└────────────────────────┬────────────────────────────────────────┘
                         │  WebSocket + REST
┌────────────────────────▼────────────────────────────────────────┐
│                     FastAPI Runtime                             │
│  POST /v1/investigate → correlation_id                          │
│  ws://localhost:8000/v1/ws/investigations/{id}                  │
└────────────────────────┬────────────────────────────────────────┘
                         │  Typed Events
┌────────────────────────▼────────────────────────────────────────┐
│                 InvestigationOrchestrator                       │
│  IntakeAgent → [Behavior│OSINT│Vision│Graph] → RiskSynthesis    │
└──────────┬──────────────────────────────────────┬──────────────┘
           │  Gateway (capability routing)         │  Event Bus
┌──────────▼──────────────┐             ┌──────────▼──────────────┐
│  AI Provider Tier        │             │  Append-Only Event Store │
│  Primary: OpenAI         │             │  PostgreSQL              │
│  Fallback: Nemotron Omni │             │  Redis realtime fanout   │
│  Last resort: Pollinations│            │  Replay + Snapshots      │
└─────────────────────────┘             └─────────────────────────┘
```

### Replay Model

```
Operator Input
    │
    ▼
EventEnvelope (append-only) ──► ReplayFrame ──► Snapshot fingerprint
    │                                               │
    ▼                                               ▼
Graph events ──► Deterministic projection ──► graph_hash verified
```

PostgreSQL stores immutable truth. Redis coordinates realtime fanout.  
Replay reconstructs investigations without re-running agents.

### Provider Routing

| Modality   | Primary      | Fallback        | Last Resort  |
|------------|-------------|-----------------|-------------|
| Text       | OpenAI      | Nemotron Omni   | Pollinations |
| Vision     | OpenAI      | Nemotron Omni   | Pollinations |
| Audio      | OpenAI      | Nemotron Omni   | —           |
| Embeddings | OpenAI      | Pollinations    | —           |

**Invocation logging:**
```
[OPENAI]      Invoking model: gpt-4.1-mini
[NVIDIA]      Invoking model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning
[POLLINATIONS] Entering degraded fallback mode
```

---

## Quickstart

### 1. Configure

```bash
cp .env.example .env
# Add OPENAI_API_KEY and NVIDIA_NIM_API_KEY
```

### 2. Boot Runtime (Docker)

```bash
docker compose up --build
```

Expected services: `api`, `postgres`, `redis` (neo4j optional)

### 3. Validate Runtime

```bash
python scripts/final_runtime_validation.py --json
```

Expected:
```json
{
  "ready": true,
  "status": {
    "postgres": "healthy",
    "redis": "healthy",
    "providers": "healthy",
    "replay": "healthy",
    "websocket": "healthy",
    "graph": "healthy"
  }
}
```

### 4. Run Demo Investigation

```bash
./scripts/demo_mode.sh telegram_onboarding_scam
```

Available scenarios:
```
telegram_onboarding_scam   — Payment coercion + Telegram onboarding
fake_internship_portal     — Phishing portal with payment gate
forged_offer_letter        — HR impersonation + document extraction
recruiter_impersonation    — Brand impersonation + urgency
coordinated_campaign       — Cross-domain campaign correlation
fake_portal_attack         — FAANG impersonation + credential harvest
```

Expected output:
```
Severity: high
Score: 66
Factors: payment_coercion, telegram_only_onboarding, osint_reputation_low, …
```

### 5. Start Flutter SOC Dashboard

```bash
cd frontend/flutter_app
flutter pub get
flutter analyze   # → No issues found
flutter test      # → All tests passed
flutter run -d linux
```

Dashboard features:
- **Severity Meter** — animated score with pulsing alert on high/critical
- **Investigation Story Mode** — numbered narrative of every agent action
- **Explainability Panel** — which evidence, which provider, which relationship
- **Threat Graph** — force-directed animated graph with severity coloring
- **Observability Panel** — live WS throughput, failover count, graph metrics
- **Replay Console** — step-through reconstruction with speed control
- **Provider Failover Badge** — animated "FAILOVER → NEMOTRON OMNI" banner

### 6. API Documentation

[http://localhost:8000/docs](http://localhost:8000/docs)

---

## WebSocket Event Stream

```
POST /v1/investigate → { "correlation_id": "INV-..." }
ws://localhost:8000/v1/ws/investigations/{correlation_id}
```

Event types:
| Event | Description |
|---|---|
| `investigation_started` | Pipeline boot |
| `agent_progress` | Agent reasoning step |
| `graph_node_added` | New entity in threat graph |
| `graph_edge_added` | New relationship in threat graph |
| `threat_escalated` | Evidence threshold crossed |
| `provider_failed` | Failover to Nemotron Omni |
| `investigation_completed` | Final verdict + score |
| `replay_verified` | Deterministic reconstruction confirmed |

---

## Structure

```
.
├── app/
│   ├── agents/          # IntakeAgent, InvestigationOrchestrator
│   ├── api/             # FastAPI transport, websocket fanout
│   ├── core/            # Settings, DI container, config
│   ├── events/          # EventEnvelope, async event bus
│   ├── gateway/         # Provider capability registry + adapters
│   │   └── providers/   # OpenAI, NVIDIA NIM, Pollinations
│   ├── graph/           # Deterministic graph projection
│   ├── models/          # ThreatScore, EvidenceSignal, BehaviorResult
│   ├── scoring/         # Evidence-weighted ThreatScoringEngine
│   └── terminal/        # Rich/Typer operator CLI
├── frontend/flutter_app/ # Flutter SOC Dashboard
│   ├── lib/dashboard/   # 3-column layout, severity meter
│   ├── lib/features/    # Investigation, graph, replay, explainability
│   └── lib/graph/       # Animated force-directed GraphCanvas
├── scripts/
│   ├── demo_mode.sh            # Cinematic scenario launcher
│   ├── final_runtime_validation.py
│   └── validate_live_providers.py
├── hermes.py            # CLI entrypoint
├── main.py              # FastAPI ASGI entrypoint
└── docker-compose.yml
```

---

## Architecture Guardrails

- Agents **never** call providers directly — all AI access goes through capability routers.
- Every AI invocation logs `[OPENAI/NVIDIA/POLLINATIONS] Invoking model: …`
- Inputs and AI outputs are schema-validated before agents process them.
- Secrets stay in environment-backed settings; never passed to agents.
- Components communicate through structured, append-only events.
- Replay is **deterministic** — no model re-invocation during reconstruction.

---

## Live Investigation Result (Demo)

```
Investigation: INV-837C1EDF
Risk: HIGH
Score: 66
Verdict: HIGH RISK — evidence includes payment_coercion, telegram_only_onboarding,
         osint_reputation_low, scarcity_tactics, recruiter_impersonation.
Graph: 3 nodes (domain, telegram, upi) | 3 edges
Replay: VERIFIED (deterministic)
```
