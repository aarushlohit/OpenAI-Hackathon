from app.replay.replay_engine import ReplaySession


class SandboxRunner:
    async def replay(self, session: ReplaySession) -> ReplaySession:
        return session.model_copy(deep=True)

