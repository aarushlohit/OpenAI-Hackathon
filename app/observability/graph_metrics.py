from dataclasses import dataclass


@dataclass(frozen=True)
class GraphMetricSnapshot:
    projections: int
    nodes: int
    edges: int
    campaigns: int
    extension_alerts: int
    autonomous_alerts: int
    replay_verifications: int
    workflow_latency_ms: int


class GraphMetrics:
    def __init__(self) -> None:
        self._projections = 0
        self._nodes = 0
        self._edges = 0
        self._campaigns = 0
        self._extension_alerts = 0
        self._autonomous_alerts = 0
        self._replay_verifications = 0
        self._workflow_latency_ms = 0

    def record_projection(self, node_count: int, edge_count: int) -> None:
        self._projections += 1
        self._nodes += node_count
        self._edges += edge_count

    def record_campaign(self) -> None:
        self._campaigns += 1

    def record_extension_alert(self) -> None:
        self._extension_alerts += 1

    def record_autonomous_alert(self) -> None:
        self._autonomous_alerts += 1

    def record_replay_verification(self) -> None:
        self._replay_verifications += 1

    def record_workflow_latency(self, latency_ms: int) -> None:
        self._workflow_latency_ms += max(latency_ms, 0)

    def snapshot(self) -> dict[str, int]:
        return GraphMetricSnapshot(
            projections=self._projections,
            nodes=self._nodes,
            edges=self._edges,
            campaigns=self._campaigns,
            extension_alerts=self._extension_alerts,
            autonomous_alerts=self._autonomous_alerts,
            replay_verifications=self._replay_verifications,
            workflow_latency_ms=self._workflow_latency_ms,
        ).__dict__
