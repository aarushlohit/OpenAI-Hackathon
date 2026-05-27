from app.gateway.models import EmbeddingRequest, EmbeddingResponse
from app.gateway.providers.base import EmbeddingProvider, ProviderFailure
from app.gateway.router_core import FailoverRouter, ProviderRoute


class EmbeddingRouter:
    def __init__(self, providers: list[EmbeddingProvider], router: FailoverRouter) -> None:
        self._providers = providers
        self._router = router

    async def embed(
        self,
        request: EmbeddingRequest,
        *,
        investigation_id: str,
        correlation_id,
    ) -> EmbeddingResponse:
        async def call(provider: EmbeddingProvider) -> EmbeddingResponse:
            try:
                return await provider.create_embedding(request)
            except ProviderFailure:
                raise

        return await self._router.execute(
            operation="embedding",
            investigation_id=investigation_id,
            correlation_id=correlation_id,
            routes=[ProviderRoute(provider.name, lambda provider=provider: call(provider)) for provider in self._providers],
        )

