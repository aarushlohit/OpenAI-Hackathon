from app.replay.replay_engine import ReplaySession


class ReplayAnalyzer:
    def analyze(self, session: ReplaySession) -> dict[str, int | bool]:
        ordered = all(
            earlier.offset_ms <= later.offset_ms
            for earlier, later in zip(session.frames, session.frames[1:], strict=False)
        )
        return {"event_count": len(session.frames), "ordered": ordered}

