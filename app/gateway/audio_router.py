from app.gateway.models import AudioTranscriptionRequest, AudioTranscriptionResponse
from app.gateway.providers.base import AudioProvider
from app.gateway.router_core import FailoverRouter, ProviderRoute


class AudioRouter:
    def __init__(self, providers: list[AudioProvider], router: FailoverRouter) -> None:
        self._providers = providers
        self._router = router

    async def transcribe(
        self,
        request: AudioTranscriptionRequest,
        *,
        investigation_id: str,
        correlation_id,
    ) -> AudioTranscriptionResponse:
        return await self._router.execute(
            operation="audio_transcription",
            investigation_id=investigation_id,
            correlation_id=correlation_id,
            routes=[
                ProviderRoute(provider.name, lambda provider=provider: provider.transcribe_audio(request))
                for provider in self._providers
            ],
        )

