from time import perf_counter

from pydantic import BaseModel, Field

from app.graph.projections import ThreatGraphProjection
from app.replay.hash_validator import HashValidator
from app.replay.replay_engine import ReplayEngine


class ReplayVerification(BaseModel):
    investigation_id: str
    verified: bool
    projection_hash: str
    graph_hash: str
    event_count: int = Field(ge=0)
    replay_duration_ms: int = Field(ge=0)


class ReplayDeterminismVerifier:
    def __init__(self, replay_engine: ReplayEngine, hash_validator: HashValidator | None = None) -> None:
        self._replay_engine = replay_engine
        self._hash_validator = hash_validator or HashValidator()

    async def verify(
        self,
        investigation_id: str,
        projection: ThreatGraphProjection | None = None,
    ) -> ReplayVerification:
        started = perf_counter()
        session = await self._replay_engine.build(investigation_id)
        projection_hash = self._hash_projection(projection)
        verified = self._hash_validator.validate_session(session)
        return ReplayVerification(
            investigation_id=investigation_id,
            verified=verified,
            projection_hash=projection_hash,
            graph_hash=projection_hash,
            event_count=len(session.frames),
            replay_duration_ms=int((perf_counter() - started) * 1000),
        )

    def _hash_projection(self, projection: ThreatGraphProjection | None) -> str:
        if projection is None:
            return ""
        return self._hash_validator.payload_hash(projection.model_dump_json())

