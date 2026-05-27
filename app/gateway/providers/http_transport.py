import logging
from time import perf_counter
from typing import Any
from uuid import uuid4

import httpx

from app.gateway.models import ProviderFailureReason
from app.gateway.providers.base import ProviderFailure

logger = logging.getLogger("hermes.gateway")

_PROVIDER_TAG: dict[str, str] = {
    "openai": "OPENAI",
    "nvidia_nim": "NVIDIA",
    "pollinations": "POLLINATIONS",
}


class ProviderHttpTransport:
    def __init__(self, provider: str, timeout_seconds: float) -> None:
        self._provider = provider
        self._timeout = timeout_seconds

    async def post_json(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], int, str]:
        tag = _PROVIDER_TAG.get(self._provider, self._provider.upper())
        model = payload.get("model", "<unknown>")
        logger.info("[%s] Invoking model: %s", tag, model)
        started = perf_counter()
        request_id = str(uuid4())
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                request_id = response.headers.get("x-request-id", request_id)
                response.raise_for_status()
                latency = self._latency(started)
                logger.info("[%s] ✓ %s responded in %dms (req=%s)", tag, model, latency, request_id)
                return response.json(), latency, request_id
        except httpx.HTTPStatusError as exc:
            logger.warning("[%s] ✗ HTTP %s — %s", tag, exc.response.status_code, exc.response.text[:120])
            raise self._map_status(exc) from exc
        except httpx.TimeoutException as exc:
            logger.warning("[%s] ✗ timeout after %ds — %s", tag, int(self._timeout), exc)
            raise ProviderFailure(self._provider, ProviderFailureReason.TIMEOUT, str(exc)) from exc
        except httpx.HTTPError as exc:
            logger.warning("[%s] ✗ network error — %s", tag, exc)
            raise ProviderFailure(self._provider, ProviderFailureReason.UNAVAILABLE, str(exc)) from exc

    async def get_text(self, url: str) -> tuple[str, int, str]:
        started = perf_counter()
        request_id = str(uuid4())
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                request_id = response.headers.get("x-request-id", request_id)
                response.raise_for_status()
                return response.text, self._latency(started), request_id
        except httpx.HTTPStatusError as exc:
            raise self._map_status(exc) from exc
        except httpx.TimeoutException as exc:
            raise ProviderFailure(self._provider, ProviderFailureReason.TIMEOUT, str(exc)) from exc
        except httpx.HTTPError as exc:
            raise ProviderFailure(self._provider, ProviderFailureReason.UNAVAILABLE, str(exc)) from exc

    def _map_status(self, error: httpx.HTTPStatusError) -> ProviderFailure:
        status = error.response.status_code
        if status == 429:
            reason = ProviderFailureReason.RATE_LIMIT
        elif status in {401, 403}:
            reason = ProviderFailureReason.AUTH
        elif status in {402, 409}:
            reason = ProviderFailureReason.QUOTA
        else:
            reason = ProviderFailureReason.UNAVAILABLE
        return ProviderFailure(self._provider, reason, error.response.text[:500])

    def _latency(self, started: float) -> int:
        return max(int((perf_counter() - started) * 1000), 0)
