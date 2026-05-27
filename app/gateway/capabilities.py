from enum import StrEnum

from pydantic import BaseModel, Field


class ProviderModality(StrEnum):
    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    EMBEDDINGS = "embeddings"


class ProviderCapability(BaseModel):
    provider: str = Field(min_length=1)
    modalities: set[ProviderModality] = Field(default_factory=set)
    streaming: bool = False
    reasoning: bool = False
    multimodal: bool = False


class ProviderCapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, ProviderCapability] = {}

    def register(self, capability: ProviderCapability) -> None:
        self._capabilities[self._normalize(capability.provider)] = capability

    def supports(self, provider: str, modality: ProviderModality) -> bool:
        capability = self._capabilities.get(self._normalize(provider))
        return capability is not None and modality in capability.modalities

    def providers_for(self, modality: ProviderModality, preferred: list[str]) -> list[str]:
        ordered: list[str] = []
        for provider in preferred:
            normalized = self._normalize(provider)
            if normalized not in ordered and self.supports(normalized, modality):
                ordered.append(normalized)
        for provider, capability in self._capabilities.items():
            if provider not in ordered and modality in capability.modalities:
                ordered.append(provider)
        return ordered

    def snapshot(self) -> dict[str, dict]:
        return {
            provider: capability.model_dump(mode="json")
            for provider, capability in self._capabilities.items()
        }

    def _normalize(self, provider: str) -> str:
        return "nvidia_nim" if provider in {"nvidia", "nim", "nvidia_nim"} else provider


def default_capability_registry() -> ProviderCapabilityRegistry:
    registry = ProviderCapabilityRegistry()
    registry.register(
        ProviderCapability(
            provider="openai",
            modalities={
                ProviderModality.TEXT,
                ProviderModality.VISION,
                ProviderModality.AUDIO,
                ProviderModality.EMBEDDINGS,
            },
            streaming=True,
        )
    )
    registry.register(
        ProviderCapability(
            provider="nvidia_nim",
            modalities={ProviderModality.TEXT, ProviderModality.VISION, ProviderModality.AUDIO},
            streaming=True,
            reasoning=True,
            multimodal=True,
        )
    )
    registry.register(
        ProviderCapability(
            provider="pollinations",
            modalities={ProviderModality.TEXT, ProviderModality.VISION, ProviderModality.EMBEDDINGS},
        )
    )
    return registry

