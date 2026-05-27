from app.gateway.models import VisionAnalysisRequest, VisionAnalysisResponse
from app.gateway.providers.base import VisionProvider
from app.gateway.router_core import FailoverRouter, ProviderRoute


class VisionRouter:
    def __init__(self, providers: list[VisionProvider], router: FailoverRouter) -> None:
        self._providers = providers
        self._router = router

    async def analyze(
        self,
        request: VisionAnalysisRequest,
        *,
        investigation_id: str,
        correlation_id,
    ) -> VisionAnalysisResponse:
        return await self._router.execute(
            operation="vision_analysis",
            investigation_id=investigation_id,
            correlation_id=correlation_id,
            routes=[
                ProviderRoute(provider.name, lambda provider=provider: provider.analyze_image(request))
                for provider in self._providers
            ],
        )
