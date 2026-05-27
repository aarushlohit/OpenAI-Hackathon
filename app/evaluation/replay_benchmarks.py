from app.replay.determinism_verifier import ReplayDeterminismVerifier, ReplayVerification


class ReplayBenchmark:
    def __init__(self, verifier: ReplayDeterminismVerifier) -> None:
        self._verifier = verifier

    async def run(self, investigation_id: str) -> ReplayVerification:
        return await self._verifier.verify(investigation_id)

