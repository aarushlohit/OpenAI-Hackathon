from app.core.config import Settings
from app.gateway.models import (
    AudioTranscriptionRequest,
    AudioTranscriptionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderFailureReason,
    TextGenerationRequest,
    TextGenerationResponse,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
)
from app.gateway.providers.base import AudioProvider, EmbeddingProvider, ProviderFailure, TextProvider, VisionProvider
from app.gateway.providers.http_transport import ProviderHttpTransport


class OpenAIProvider(TextProvider, VisionProvider, AudioProvider, EmbeddingProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._transport = ProviderHttpTransport(self.name, settings.ai_request_timeout_seconds)

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        if self._settings.openai_api_key is None:
            raise ProviderFailure(self.name, ProviderFailureReason.AUTH, "OpenAI key is not configured")
        raw, latency_ms, request_id = await self._transport.post_json(
            "https://api.openai.com/v1/responses",
            headers=self._headers(),
            payload={
                "model": self._settings.openai_text_model,
                "instructions": request.system_prompt,
                "input": request.user_prompt,
                "temperature": request.temperature,
            },
        )
        return TextGenerationResponse(
            provider=self.name,
            model=self._settings.openai_text_model,
            content=self._extract_response_text(raw),
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
        )

    async def analyze_image(self, request: VisionAnalysisRequest) -> VisionAnalysisResponse:
        if self._settings.openai_api_key is None:
            raise ProviderFailure(self.name, ProviderFailureReason.AUTH, "OpenAI key is not configured")
        raw, latency_ms, request_id = await self._transport.post_json(
            "https://api.openai.com/v1/responses",
            headers=self._headers(),
            payload={
                "model": self._settings.openai_vision_model,
                "instructions": request.system_prompt,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": request.user_prompt},
                            {"type": "input_image", "image_url": request.image_reference},
                        ],
                    }
                ],
            },
        )
        return VisionAnalysisResponse(
            provider=self.name,
            model=self._settings.openai_vision_model,
            content=self._extract_response_text(raw),
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
        )

    async def transcribe_audio(self, request: AudioTranscriptionRequest) -> AudioTranscriptionResponse:
        if self._settings.openai_api_key is None:
            raise ProviderFailure(self.name, ProviderFailureReason.AUTH, "OpenAI key is not configured")
        raise ProviderFailure(self.name, ProviderFailureReason.UNAVAILABLE, "OpenAI audio requires file upload wiring")

    async def create_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        if self._settings.openai_api_key is None:
            raise ProviderFailure(self.name, ProviderFailureReason.AUTH, "OpenAI key is not configured")
        payload = {"model": self._settings.openai_embedding_model, "input": request.content}
        if request.dimensions is not None:
            payload["dimensions"] = request.dimensions
        raw, latency_ms, request_id = await self._transport.post_json(
            "https://api.openai.com/v1/embeddings",
            headers=self._headers(),
            payload=payload,
        )
        vector = raw.get("data", [{}])[0].get("embedding")
        if not isinstance(vector, list):
            raise ProviderFailure(self.name, ProviderFailureReason.INVALID_RESPONSE, "missing embedding vector")
        return EmbeddingResponse(
            provider=self.name,
            model=self._settings.openai_embedding_model,
            content="embedding",
            confidence=None,
            latency_ms=latency_ms,
            tokens_used=self._extract_tokens(raw),
            success=True,
            request_id=request_id,
            raw_response=raw,
            vector=vector,
        )

    def _headers(self) -> dict[str, str]:
        key = self._settings.openai_api_key
        return {"Authorization": f"Bearer {key.get_secret_value()}", "Content-Type": "application/json"}

    def _extract_response_text(self, raw: dict) -> str:
        text = raw.get("output_text")
        if isinstance(text, str) and text.strip():
            return text
        for output in raw.get("output", []):
            for item in output.get("content", []):
                if item.get("type") in {"output_text", "text"} and item.get("text"):
                    return str(item["text"])
        raise ProviderFailure(self.name, ProviderFailureReason.INVALID_RESPONSE, "missing response text")

    def _extract_tokens(self, raw: dict) -> int | None:
        usage = raw.get("usage")
        if not isinstance(usage, dict):
            return None
        total = usage.get("total_tokens") or usage.get("total")
        return int(total) if isinstance(total, int) else None
