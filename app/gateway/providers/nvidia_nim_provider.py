from app.core.config import Settings
from app.gateway.models import (
    AudioTranscriptionRequest,
    AudioTranscriptionResponse,
    ProviderFailureReason,
    TextGenerationRequest,
    TextGenerationResponse,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
)
from app.gateway.providers.base import AudioProvider, ProviderFailure, TextProvider, VisionProvider
from app.gateway.providers.http_transport import ProviderHttpTransport


class NvidiaNimProvider(TextProvider, VisionProvider, AudioProvider):
    name = "nvidia_nim"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._transport = ProviderHttpTransport(self.name, settings.ai_request_timeout_seconds)

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        if self._settings.nvidia_nim_api_key is None:
            raise ProviderFailure(self.name, ProviderFailureReason.AUTH, "NVIDIA NIM key is not configured")
        raw, latency_ms, request_id = await self._transport.post_json(
            f"{str(self._settings.nvidia_nim_base_url).rstrip('/')}/chat/completions",
            headers=self._headers(),
            payload={
                "model": self._settings.nvidia_nim_text_model,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                "temperature": request.temperature,
            },
        )
        return TextGenerationResponse(
            provider=self.name,
            model=self._settings.nvidia_nim_text_model,
            content=self._extract_chat_text(raw),
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
        )

    async def analyze_image(self, request: VisionAnalysisRequest) -> VisionAnalysisResponse:
        if self._settings.nvidia_nim_api_key is None:
            raise ProviderFailure(self.name, ProviderFailureReason.AUTH, "NVIDIA NIM key is not configured")
        raw, latency_ms, request_id = await self._transport.post_json(
            f"{str(self._settings.nvidia_nim_base_url).rstrip('/')}/chat/completions",
            headers=self._headers(),
            payload={
                "model": self._settings.nvidia_nim_vision_model,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": request.user_prompt},
                            {"type": "image_url", "image_url": {"url": request.image_reference}},
                        ],
                    },
                ],
            },
        )
        return VisionAnalysisResponse(
            provider=self.name,
            model=self._settings.nvidia_nim_vision_model,
            content=self._extract_chat_text(raw),
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
        )

    async def transcribe_audio(self, request: AudioTranscriptionRequest) -> AudioTranscriptionResponse:
        if self._settings.nvidia_nim_api_key is None:
            raise ProviderFailure(self.name, ProviderFailureReason.AUTH, "NVIDIA NIM key is not configured")
        raw, latency_ms, request_id = await self._transport.post_json(
            f"{str(self._settings.nvidia_nim_base_url).rstrip('/')}/chat/completions",
            headers=self._headers(),
            payload={
                "model": self._settings.nvidia_nim_audio_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Analyze the supplied audio reference and return concise transcript evidence.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Transcribe and summarize this audio artifact."},
                            {"type": "audio_url", "audio_url": {"url": request.audio_reference}},
                        ],
                    },
                ],
            },
        )
        return AudioTranscriptionResponse(
            provider=self.name,
            model=self._settings.nvidia_nim_audio_model,
            content=self._extract_chat_text(raw),
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
        )

    def _headers(self) -> dict[str, str]:
        key = self._settings.nvidia_nim_api_key
        return {"Authorization": f"Bearer {key.get_secret_value()}", "Content-Type": "application/json"}

    def _extract_chat_text(self, raw: dict) -> str:
        content = raw.get("choices", [{}])[0].get("message", {}).get("content")
        if isinstance(content, str) and content.strip():
            return content
        raise ProviderFailure(self.name, ProviderFailureReason.INVALID_RESPONSE, "missing chat content")

    def _extract_tokens(self, raw: dict) -> int | None:
        usage = raw.get("usage")
        if not isinstance(usage, dict):
            return None
        total = usage.get("total_tokens")
        return int(total) if isinstance(total, int) else None
