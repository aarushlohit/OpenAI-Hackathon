# Security

Hermes-X uses zero-trust security assumptions.

Never trust:

- Uploaded documents.
- PDFs or office files.
- URLs and redirects.
- Screenshots and images.
- Prompt content.
- AI model output.
- Claimed recruiter identity.

Controls:

- Input validation occurs before orchestration.
- Secrets are loaded through Pydantic settings as secret values.
- Agents do not receive provider credentials.
- Provider clients are isolated behind gateway routers.
- AI responses must be schema-validated before use in decisions.
- Future artifact processing must run in sandboxed workers.

Security failures should fail closed and emit structured events.

Phase 8 hardening:

- Event schema hashes support tamper detection.
- Security audit mode checks append-only ordering and schema hash consistency.
- Websocket authorization boundaries are represented by `WebsocketAuthorizer`.
- Rate limiting primitives are available for API hardening.

Phase 8.5 hardening:

- Snapshot integrity checks certify replay state.
- Dead-letter queue preserves corrupt or unauthorized events for inspection.
- Trace context supports spoof detection and workflow lineage.
- Sandbox replay enables evaluation without mutating live projections.

Phase 9 hardening:

- PostgreSQL persistence stores governed event envelopes with schema hashes, producers, trace context, and append-only ordering.
- Redis channels are constrained to the `hermes:` namespace.
- Bootstrap checks fail readiness when required runtime dependencies are unavailable.
- Database integrity verification can hash persisted event chains for tamper detection.

Phase 10 hardening:

- Provider priority is environment-driven and capability-checked before routing.
- Provider secrets remain in settings and are never exposed to agents or websocket clients.
- Websocket payloads carry trace context for replay and spoof investigation.
- Final validation can run in strict mode during deployment gates.

MVP ship-mode hardening:

- Reset scripts preserve volumes by default and require `CONFIRM_RESET=YES` for destructive volume removal.
- Live provider validation masks secrets and prints only provider status.
- Flutter remains a presentation layer and never receives provider keys.
- Runtime startup scripts validate configuration without embedding secrets.
