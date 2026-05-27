# Graph Architecture

Hermes-X threat graph intelligence converts investigation context into deterministic graph projections.

Components:

- `ThreatGraphEngine`: projection coordinator.
- `GraphNodeBuilder`: converts extracted entities into typed graph nodes.
- `GraphEdgeBuilder`: creates deterministic investigation-to-entity edges.
- `RelationshipRules`: maps entity kinds to relationship types.
- `GraphRepository`: graph persistence abstraction.
- `InMemoryGraphRepository`: local adapter for tests and development.

Supported entities:

- Domains.
- Recruiter emails.
- Telegram handles.
- UPI IDs.
- Phone numbers.
- Company aliases.
- Offer-letter signatures.
- Recruiter names.
- Payment wallets.

Rules:

- No direct Neo4j coupling.
- Projections must be rebuildable from context and events.
- Graph events must be safe to serialize over websocket.
- UI clients render graph state but do not infer relationships.

Operational extensions:

- Graph growth contributes to operational metrics.
- Autonomous monitoring can use graph-backed threat memory to detect repeated campaign entities.
- Lineage tracking links campaigns and inherited evidence without mutating graph history.
