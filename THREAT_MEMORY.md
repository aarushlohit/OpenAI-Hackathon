# Threat Memory

Threat memory stores recurring scam entities and investigation relationships.

Components:

- `EntityIndex`: maps entities to related investigation IDs.
- `ThreatMemory`: stores graph projections and enriches lookups.
- `GraphRepository`: stores per-investigation graph projections.

Goals:

- Adaptive intelligence.
- Repeated pattern detection.
- Campaign evolution tracking.
- Threat replay analysis.

Threat memory is currently in-memory and repository-backed so a future graph database can be added without changing agents or orchestrator contracts.

