# SOC Operations

Phase 7 introduces SOC-grade operational surfaces while keeping intelligence backend-side.

Operational views:

- Active threat campaigns.
- Live investigations.
- Graph cluster activity.
- Threat feed.
- Provider infrastructure status.
- Extension alert activity.
- Severity heatmap.

Flutter panels render event and metric projections only. They do not route workflows, score investigations, or infer graph relationships.

Production readiness:

- SOC views should surface schema drift, replay verification failures, autonomous alert frequency, and workflow bottlenecks.
- Phase 10 SOC views should also surface provider capability status, runtime validation state, Redis/PostgreSQL health, and failover activity.
