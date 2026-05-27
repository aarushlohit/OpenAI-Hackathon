from collections.abc import Iterable
from typing import Protocol, TypeVar

from app.core.config import Settings
from app.gateway.capabilities import ProviderCapabilityRegistry, ProviderModality


class NamedProvider(Protocol):
    name: str


ProviderT = TypeVar("ProviderT", bound=NamedProvider)


class ProviderPriorityResolver:
    def __init__(self, settings: Settings, capabilities: ProviderCapabilityRegistry) -> None:
        self._settings = settings
        self._capabilities = capabilities

    def order(self, modality: ProviderModality, providers: Iterable[ProviderT]) -> list[ProviderT]:
        by_name = {self._normalize(provider.name): provider for provider in providers}
        configured = self._configured_order(modality)
        ordered_names = self._capabilities.providers_for(modality, configured)
        return [by_name[name] for name in ordered_names if name in by_name]

    def _configured_order(self, modality: ProviderModality) -> list[str]:
        if modality == ProviderModality.TEXT:
            return [
                self._settings.primary_text_provider,
                self._settings.fallback_text_provider,
                self._settings.last_resort_text_provider,
            ]
        if modality == ProviderModality.VISION:
            return [
                self._settings.primary_vision_provider,
                self._settings.fallback_vision_provider,
                self._settings.last_resort_vision_provider,
            ]
        if modality == ProviderModality.AUDIO:
            return [self._settings.primary_audio_provider, self._settings.fallback_audio_provider]
        return [self._settings.primary_embedding_provider, self._settings.fallback_embedding_provider]

    def _normalize(self, provider: str) -> str:
        return "nvidia_nim" if provider in {"nvidia", "nim", "nvidia_nim"} else provider
