from app.replay.snapshot_builder import ReplaySnapshot


class SnapshotValidator:
    def validate(self, left: ReplaySnapshot, right: ReplaySnapshot) -> bool:
        return (
            left.projection_hash == right.projection_hash
            and left.graph_hash == right.graph_hash
            and left.timeline_hash == right.timeline_hash
            and left.investigation_lineage_hash == right.investigation_lineage_hash
        )

