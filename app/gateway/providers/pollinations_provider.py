from app.core.config import Settings
from app.gateway.models import (
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderFailureReason,
    TextGenerationRequest,
    TextGenerationResponse,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
)
from app.gateway.providers.base import EmbeddingProvider, ProviderFailure, TextProvider, VisionProvider
from urllib.parse import quote

from app.gateway.providers.http_transport import ProviderHttpTransport


class PollinationsProvider(TextProvider, VisionProvider, EmbeddingProvider):
    name = "pollinations"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._transport = ProviderHttpTransport(self.name, settings.ai_request_timeout_seconds)

    async def analyze_image(self, request: VisionAnalysisRequest) -> VisionAnalysisResponse:
        raw, latency_ms, request_id = await self._transport.post_json(
            str(self._settings.pollinations_chat_url),
            headers={"Content-Type": "application/json"},
            payload={
                "model": self._settings.pollinations_vision_model,
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
            model=self._settings.pollinations_vision_model,
            content=self._extract_chat_text(raw),
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
        )

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        raw, latency_ms, request_id = await self._transport.post_json(
            str(self._settings.pollinations_chat_url),
            headers={"Content-Type": "application/json"},
            payload={
                "model": self._settings.pollinations_text_model,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                "temperature": request.temperature,
            },
        )
        return TextGenerationResponse(
            provider=self.name,
            model=self._settings.pollinations_text_model,
            content=self._extract_chat_text(raw),
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
        )

    async def create_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise ProviderFailure(self.name, ProviderFailureReason.UNAVAILABLE, "Pollinations embedding endpoint not configured")

    def _extract_chat_text(self, raw: dict) -> str:
        content = raw.get("choices", [{}])[0].get("message", {}).get("content")
        if isinstance(content, str) and content.strip():
            return content
        text = raw.get("output_text")
        if isinstance(text, str) and text.strip():
            return text
        raise ProviderFailure(self.name, ProviderFailureReason.INVALID_RESPONSE, "missing chat content")

    def _extract_tokens(self, raw: dict) -> int | None:
        usage = raw.get("usage")
        if not isinstance(usage, dict):
            return None
        total = usage.get("total_tokens")
        return int(total) if isinstance(total, int) else None

    async def generate_legacy_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        prompt = f"{request.system_prompt}\n\n{request.user_prompt}"
        url = f"{str(self._settings.pollinations_base_url).rstrip('/')}/{quote(prompt, safe='')}"
        content, latency_ms, request_id = await self._transport.get_text(url)
        if not content.strip():
            raise ProviderFailure(self.name, ProviderFailureReason.INVALID_RESPONSE, "empty Pollinations response")
        return TextGenerationResponse(
            provider=self.name,
            model=self._settings.pollinations_text_model,
            content=content,
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=None,
            success=True,
            request_id=request_id,
            raw_response={"transport": "legacy_text"},
        )
