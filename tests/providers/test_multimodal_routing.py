import unittest

from app.core.config import Settings
from app.gateway.capabilities import ProviderModality, default_capability_registry
from app.gateway.provider_priority import ProviderPriorityResolver


class Provider:
    def __init__(self, name: str) -> None:
        self.name = name


class MultimodalRoutingTests(unittest.TestCase):
    def test_text_routing_uses_environment_priority(self) -> None:
        resolver = ProviderPriorityResolver(
            Settings(
                primary_text_provider="nvidia",
                fallback_text_provider="openai",
                last_resort_text_provider="pollinations",
            ),
            default_capability_registry(),
        )

        ordered = resolver.order(
            ProviderModality.TEXT,
            [Provider("openai"), Provider("nvidia_nim"), Provider("pollinations")],
        )

        self.assertEqual([provider.name for provider in ordered], ["nvidia_nim", "openai", "pollinations"])

    def test_audio_routing_excludes_pollinations(self) -> None:
        resolver = ProviderPriorityResolver(Settings(), default_capability_registry())

        ordered = resolver.order(
            ProviderModality.AUDIO,
            [Provider("openai"), Provider("nvidia_nim"), Provider("pollinations")],
        )

        self.assertEqual([provider.name for provider in ordered], ["openai", "nvidia_nim"])


if __name__ == "__main__":
    unittest.main()

