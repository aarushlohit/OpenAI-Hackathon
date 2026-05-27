from typing import overload

from app.gateway.audio_router import AudioRouter
from app.gateway.capabilities import ProviderModality
from app.gateway.embedding_router import EmbeddingRouter
from app.gateway.models import (
    AudioTranscriptionRequest,
    AudioTranscriptionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    TextGenerationRequest,
    TextGenerationResponse,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
)
from app.gateway.text_router import TextRouter
from app.gateway.vision_router import VisionRouter


class MultimodalRouter:
    def __init__(
        self,
        text: TextRouter,
        vision: VisionRouter,
        audio: AudioRouter,
        embeddings: EmbeddingRouter,
    ) -> None:
        self._text = text
        self._vision = vision
        self._audio = audio
        self._embeddings = embeddings

    @overload
    async def route(
        self,
        modality: ProviderModality,
        request: TextGenerationRequest,
        *,
        investigation_id: str,
        correlation_id,
    ) -> TextGenerationResponse: ...

    @overload
    async def route(
        self,
        modality: ProviderModality,
        request: VisionAnalysisRequest,
        *,
        investigation_id: str,
        correlation_id,
    ) -> VisionAnalysisResponse: ...

    async def route(self, modality, request, *, investigation_id: str, correlation_id):
        if modality == ProviderModality.TEXT:
            return await self._text.generate(request, investigation_id=investigation_id, correlation_id=correlation_id)
        if modality == ProviderModality.VISION:
            return await self._vision.analyze(request, investigation_id=investigation_id, correlation_id=correlation_id)
        if modality == ProviderModality.AUDIO:
            return await self._audio.transcribe(request, investigation_id=investigation_id, correlation_id=correlation_id)
        if modality == ProviderModality.EMBEDDINGS:
            return await self._embeddings.embed(request, investigation_id=investigation_id, correlation_id=correlation_id)
        raise ValueError(f"Unsupported modality: {modality}")
