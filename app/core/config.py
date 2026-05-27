from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "app/.env"), env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "staging", "production"] = "development"
    log_level: str = "INFO"

    openai_api_key: SecretStr | None = None
    openai_text_model: str = "gpt-4.1-mini"
    openai_vision_model: str = "gpt-4.1-mini"
    openai_audio_model: str = "gpt-4o-transcribe"
    openai_embedding_model: str = "text-embedding-3-small"

    nvidia_nim_api_key: SecretStr | None = None
    nvidia_nim_base_url: AnyUrl = "https://integrate.api.nvidia.com/v1"
    nvidia_nim_text_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    nvidia_nim_vision_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    nvidia_nim_audio_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"

    pollinations_base_url: AnyUrl = "https://text.pollinations.ai"
    pollinations_chat_url: AnyUrl = "https://gen.pollinations.ai/v1/chat/completions"
    pollinations_text_model: str = "openai"
    pollinations_vision_model: str = "openai"
    pollinations_embedding_model: str = "openai"

    postgres_dsn: str = "postgresql+asyncpg://hermes:hermes@localhost:5432/hermes_x"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: SecretStr | None = None
    redis_dsn: str = "redis://localhost:6379/0"

    primary_text_provider: str = "openai"
    fallback_text_provider: str = "nvidia"
    last_resort_text_provider: str = "pollinations"
    primary_vision_provider: str = "openai"
    fallback_vision_provider: str = "nvidia"
    last_resort_vision_provider: str = "pollinations"
    primary_audio_provider: str = "openai"
    fallback_audio_provider: str = "nvidia"
    primary_embedding_provider: str = "openai"
    fallback_embedding_provider: str = "pollinations"

    ai_request_timeout_seconds: float = Field(default=30.0, gt=0)
    ai_max_retries: int = Field(default=2, ge=0, le=5)
    agent_timeout_seconds: float = Field(default=15.0, gt=0, le=120)
    provider_circuit_failure_threshold: int = Field(default=3, ge=1, le=20)
    provider_circuit_recovery_seconds: int = Field(default=60, ge=5, le=3600)
    event_stream_buffer_size: int = Field(default=500, ge=10, le=10_000)
    runtime_enable_redis_client: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
