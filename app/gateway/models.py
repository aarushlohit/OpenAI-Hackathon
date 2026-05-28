from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ProviderFailureReason(StrEnum):
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    QUOTA = "quota"
    AUTH = "auth"
    UNAVAILABLE = "unavailable"
    INVALID_RESPONSE = "invalid_response"
    CIRCUIT_OPEN = "circuit_open"


class ProviderResponse(BaseModel):
    provider: str
    model: str
    content: str = Field(min_length=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    latency_ms: int = Field(ge=0)
    tokens_used: int | None = Field(default=None, ge=0)
    success: bool
    request_id: str = Field(min_length=1, max_length=120)
    raw_response: dict[str, Any] | None = None


class TextGenerationRequest(BaseModel):
    system_prompt: str = Field(min_length=1, max_length=8_000)
    user_prompt: str = Field(min_length=1, max_length=40_000)
    response_schema: dict[str, Any] | None = None
    temperature: float = Field(default=0.1, ge=0, le=1)


class TextGenerationResponse(ProviderResponse):
    pass


class VisionAnalysisRequest(BaseModel):
    system_prompt: str = Field(min_length=1, max_length=8_000)
    user_prompt: str = Field(min_length=1, max_length=20_000)
    image_reference: str = Field(min_length=1, max_length=2_000)
    response_schema: dict[str, Any] | None = None


class VisionAnalysisResponse(ProviderResponse):
    pass


class AudioTranscriptionRequest(BaseModel):
    audio_reference: str = Field(min_length=1, max_length=2_000)
    language_hint: str | None = Field(default=None, min_length=2, max_length=32)
    response_schema: dict[str, Any] | None = None


class AudioTranscriptionResponse(ProviderResponse):
    pass


class AudioAnalysisRequest(BaseModel):
    system_prompt: str = Field(min_length=1, max_length=8_000)
    user_prompt: str = Field(min_length=1, max_length=20_000)
    audio_reference: str = Field(min_length=1, max_length=2_000)
    response_schema: dict[str, Any] | None = None
    language_hint: str | None = Field(default=None, min_length=2, max_length=32)


class AudioAnalysisResponse(ProviderResponse):
    pass


class EmbeddingRequest(BaseModel):
    content: str = Field(min_length=1, max_length=40_000)
    dimensions: int | None = Field(default=None, ge=128, le=4096)


class EmbeddingResponse(ProviderResponse):
    vector: list[float] = Field(min_length=1)
