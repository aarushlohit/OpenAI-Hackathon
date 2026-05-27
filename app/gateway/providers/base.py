from abc import ABC, abstractmethod

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


class ProviderFailure(Exception):
    def __init__(self, provider: str, reason: ProviderFailureReason, detail: str) -> None:
        super().__init__(detail)
        self.provider = provider
        self.reason = reason
        self.detail = detail


class TextProvider(ABC):
    name: str

    @abstractmethod
    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        raise NotImplementedError


class VisionProvider(ABC):
    name: str

    @abstractmethod
    async def analyze_image(self, request: VisionAnalysisRequest) -> VisionAnalysisResponse:
        raise NotImplementedError


class AudioProvider(ABC):
    name: str

    @abstractmethod
    async def transcribe_audio(self, request: AudioTranscriptionRequest) -> AudioTranscriptionResponse:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    name: str

    @abstractmethod
    async def create_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise NotImplementedError
