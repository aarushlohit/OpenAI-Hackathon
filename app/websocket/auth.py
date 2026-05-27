from uuid import UUID


class WebsocketAuthorizer:
    def authorize(self, correlation_id: UUID, token: str | None = None) -> bool:
        return bool(correlation_id) and (token is None or len(token) >= 8)

