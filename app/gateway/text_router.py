from app.gateway.models import TextGenerationRequest, TextGenerationResponse
from app.gateway.providers.base import TextProvider
from app.gateway.router_core import FailoverRouter, ProviderRoute


class TextRouter:
    def __init__(self, providers: list[TextProvider], router: FailoverRouter) -> None:
        self._providers = providers
        self._router = router

    async def generate(
        self,
        request: TextGenerationRequest,
        *,
        investigation_id: str,
        correlation_id,
    ) -> TextGenerationResponse:
        return await self._router.execute(
            operation="text_generation",
            investigation_id=investigation_id,
            correlation_id=correlation_id,
            routes=[
                ProviderRoute(provider.name, lambda provider=provider: provider.generate_text(request))
                for provider in self._providers
            ],
        )
