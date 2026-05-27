from pydantic import BaseModel, Field

from app.graph.projections import ThreatGraphProjection
from app.replay.replay_engine import ReplaySession
from app.replay.state_fingerprint import StateFingerprint


class ReplaySnapshot(BaseModel):
    investigation_id: str
    event_range: tuple[int, int]
    projection_hash: str
    graph_hash: str
    timeline_hash: str
    investigation_lineage_hash: str
    schema_versions: dict[str, str] = Field(default_factory=dict)


class SnapshotBuilder:
    def __init__(self, fingerprint: StateFingerprint | None = None) -> None:
        self._fingerprint = fingerprint or StateFingerprint()

    def build(
        self,
        session: ReplaySession,
        projection: ThreatGraphProjection | None = None,
        lineage: dict | None = None,
    ) -> ReplaySnapshot:
        event_range = (0, max(len(session.frames) - 1, 0))
        projection_payload = {} if projection is None else projection.model_dump(mode="json")
        timeline_payload = [frame.event.safe_payload() for frame in session.frames]
        schema_versions = {frame.event.event.value: frame.event.event_version for frame in session.frames}
        return ReplaySnapshot(
            investigation_id=session.investigation_id,
            event_range=event_range,
            projection_hash=self._fingerprint.hash_json(projection_payload),
            graph_hash=self._fingerprint.hash_json(projection_payload),
            timeline_hash=self._fingerprint.hash_json(timeline_payload),
            investigation_lineage_hash=self._fingerprint.hash_json(lineage or {}),
            schema_versions=schema_versions,
        )

