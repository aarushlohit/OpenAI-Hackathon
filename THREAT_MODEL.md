# Threat Model

Primary adversaries:

- Fake recruiters targeting students.
- Phishing operators collecting credentials or payments.
- Impersonators using real company branding.
- Malware distributors hiding payloads in offer letters.
- Prompt attackers attempting to control agents through submitted content.

High-risk assets:

- Student identity data.
- Uploaded documents and screenshots.
- Investigation conclusions.
- API keys and provider credentials.
- Institutional trust decisions.

Phase 1 mitigations:

- Zero-trust intake policy.
- Provider isolation.
- Schema-first event contracts.
- No direct artifact execution.
- No frontend upload surface.

Phase 2+ mitigations:

- Provider routing uses centralized retries and circuit breaker checks.
- Investigation IDs support incident tracking without exposing internal UUIDs.
- Observability captures provider failures and latency patterns for abuse detection.

Phase 3 mitigations:

- Agents produce evidence, not final verdicts.
- Threat scoring is centralized and explainable.
- OCR sanitization removes control characters before analysis.
- AI output validation supports malformed JSON recovery and injection filtering.
- Realtime events expose investigation progress for human oversight.

Phase 6 mitigations:

- Graph payloads are typed before websocket serialization.
- Protection API lookups are backed by threat memory, not extension-supplied conclusions.
- Sentinel validates extension messages before making lookups.
- Graph repositories remain abstract to avoid direct database coupling.

Phase 7 mitigations:

- Replay frames include integrity hashes.
- Autonomous monitoring emits new events instead of mutating historical investigations.
- Demo cinema frames use the normal event bus and remain separate from production scoring.
- Executive reporting consumes existing scores without recomputation.

Phase 8 mitigations:

- Event schema hashes detect malformed or drifted payloads.
- Replay determinism verifier checks replay consistency before trust.
- Agent contracts constrain emitted events, workflows, and actions.
- Security audit mode checks append-only ordering and schema hash consistency.

Phase 8.5 mitigations:

- Runtime health exposes degraded dependencies.
- Dead-letter queues quarantine malformed events.
- Snapshot validation detects replay divergence.
- Trace context improves spoof detection.

Phase 10 mitigations:

- Capability-driven provider routing prevents unsupported modality calls from being selected.
- Provider priority is configuration-driven and still isolated behind gateway routers.
- Websocket events include trace metadata for replay lineage review.
- Runtime validation supports strict deployment gates.

Residual risks:

- Live provider integrations require real credentials and network validation in the deployment environment.
- OpenAI audio upload support remains constrained by safe artifact handling requirements.
- Sandboxed file detonation is deferred to Phase 2.
