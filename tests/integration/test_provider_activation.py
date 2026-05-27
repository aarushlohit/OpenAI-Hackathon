import unittest

from app.core.config import Settings
from app.gateway.models import ProviderFailureReason, TextGenerationRequest
from app.gateway.providers.base import ProviderFailure
from app.gateway.providers.openai_provider import OpenAIProvider


class ProviderActivationTests(unittest.IsolatedAsyncioTestCase):
    async def test_openai_provider_fails_closed_without_key(self) -> None:
        provider = OpenAIProvider(Settings(openai_api_key=None))

        with self.assertRaises(ProviderFailure) as raised:
            await provider.generate_text(
                TextGenerationRequest(system_prompt="Return JSON.", user_prompt="Analyze this.")
            )

        self.assertEqual(raised.exception.reason, ProviderFailureReason.AUTH)


if __name__ == "__main__":
    unittest.main()
