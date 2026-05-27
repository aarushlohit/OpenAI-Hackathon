import asyncio
from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import TypeVar

from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName
from app.gateway.models import ProviderFailureReason, ProviderResponse
from app.gateway.providers.base import ProviderFailure
from app.observability import CircuitBreaker, ProviderMetrics, ProviderTrace

ResponseT = TypeVar("ResponseT", bound=ProviderResponse)
ProviderCall = Callable[[], Awaitable[ResponseT]]


class ProviderRoute[ResponseT: ProviderResponse]:
    def __init__(self, provider_name: str, call: ProviderCall[ResponseT]) -> None:
        self.provider_name = provider_name
        self.call = call


class FailoverRouter:
    def __init__(
        self,
        event_bus: InMemoryEventBus,
        circuit_breaker: CircuitBreaker,
        metrics: ProviderMetrics,
        max_retries: int,
    ) -> None:
        self._event_bus = event_bus
        self._circuit_breaker = circuit_breaker
        self._metrics = metrics
        self._max_retries = max_retries

    async def execute(
        self,
        *,
        operation: str,
        investigation_id: str,
        correlation_id,
        routes: list[ProviderRoute[ResponseT]],
    ) -> ResponseT:
        last_failure: ProviderFailure | None = None
        for provider_index, route in enumerate(routes):
            if not self._circuit_breaker.allow_request(route.provider_name):
                await self._emit_failure(
                    correlation_id=correlation_id,
                    provider=route.provider_name,
                    reason=ProviderFailureReason.CIRCUIT_OPEN,
                    detail="Provider circuit is open",
                )
                continue

            for attempt in range(self._max_retries + 1):
                started = perf_counter()
                try:
                    response = await route.call()
                    latency_ms = int((perf_counter() - started) * 1000)
                    self._circuit_breaker.record_success(route.provider_name)
                    self._metrics.record(
                        ProviderTrace(
                            investigation_id=investigation_id,
                            request_id=response.request_id,
                            provider=response.provider,
                            operation=operation,
                            latency_ms=latency_ms,
                            success=True,
                        )
                    )
                    if provider_index > 0:
                        await self._event_bus.publish(
                            EventEnvelope(
                                event=EventName.PROVIDER_FAILOVER,
                                correlation_id=correlation_id,
                                payload={"provider": route.provider_name, "operation": operation},
                            )
                        )
                    return response
                except ProviderFailure as failure:
                    last_failure = failure
                    self._circuit_breaker.record_failure(route.provider_name)
                    latency_ms = int((perf_counter() - started) * 1000)
                    self._metrics.record(
                        ProviderTrace(
                            investigation_id=investigation_id,
                            request_id=investigation_id,
                            provider=route.provider_name,
                            operation=operation,
                            latency_ms=latency_ms,
                            success=False,
                            failure_reason=failure.reason.value,
                        )
                    )
                    await self._emit_failure(
                        correlation_id=correlation_id,
                        provider=failure.provider,
                        reason=failure.reason,
                        detail=failure.detail,
                    )
                    if attempt < self._max_retries:
                        await asyncio.sleep(0)
        raise RuntimeError(f"All {operation} providers failed: {last_failure}") from last_failure

    async def _emit_failure(
        self,
        *,
        correlation_id,
        provider: str,
        reason: ProviderFailureReason,
        detail: str,
    ) -> None:
        await self._event_bus.publish(
            EventEnvelope(
                event=EventName.PROVIDER_FAILED,
                correlation_id=correlation_id,
                payload={"provider": provider, "reason": reason.value, "detail": detail},
            )
        )
