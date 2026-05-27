import unittest
from uuid import uuid4

from app.events.bus import InMemoryEventBus
from app.gateway.models import ProviderFailureReason, TextGenerationRequest, TextGenerationResponse
from app.gateway.providers.base import ProviderFailure, TextProvider
from app.gateway.router_core import FailoverRouter
from app.gateway.text_router import TextRouter
from app.observability import CircuitBreaker, ProviderMetrics


class FailingTextProvider(TextProvider):
    name = "primary"

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        raise ProviderFailure(self.name, ProviderFailureReason.TIMEOUT, "timeout")


class PassingTextProvider(TextProvider):
    name = "fallback"

    async def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        return TextGenerationResponse(
            provider=self.name,
            model="test",
            content="ok",
            latency_ms=1,
            success=True,
            request_id="req-1",
        )


class FailoverTests(unittest.IsolatedAsyncioTestCase):
    async def test_text_router_uses_fallback(self) -> None:
        event_bus = InMemoryEventBus()
        router = TextRouter(
            providers=[FailingTextProvider(), PassingTextProvider()],
            router=FailoverRouter(
                event_bus=event_bus,
                circuit_breaker=CircuitBreaker(),
                metrics=ProviderMetrics(),
                max_retries=0,
            ),
        )

        result = await router.generate(
            TextGenerationRequest(system_prompt="system", user_prompt="user"),
            investigation_id="INV-ABCDEF12",
            correlation_id=uuid4(),
        )

        self.assertEqual(result.provider, "fallback")
