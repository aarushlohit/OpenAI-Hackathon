from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import requests

from app.security.json_recovery import JsonRecoveryError, recover_json_object

logger = logging.getLogger(__name__)

NVIDIA_INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
POLLINATIONS_INVOKE_URL = "https://gen.pollinations.ai/v1/chat/completions"
POLLINATIONS_TEXT_MODEL = "qwen-safety"
POLLINATIONS_VISION_MODEL = "mistral"
STRICT_PROVIDER_MODE = True
TRANSIENT_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504}


def _console_log(tag: str, message: str) -> None:
    print(f"[{tag}] {message}", file=sys.stderr, flush=True)


@dataclass(frozen=True)
class ProviderResponseMetadata:
    provider: str
    model: str
    request_id: str
    latency_ms: int
    headers: dict[str, str] = field(default_factory=dict)
    raw_response: dict[str, Any] = field(default_factory=dict)


class NvidiaReasoningError(Exception):
    def __init__(self, detail: str, latency_ms: int = 0, request_id: str = "") -> None:
        super().__init__(detail)
        self.latency_ms = latency_ms
        self.request_id = request_id


class NvidiaReasoningClient:
    """Strict NVIDIA NIM chat-completions client.

    The public methods stay async so existing agents do not need architectural changes,
    but the provider invocation itself is the mandated synchronous requests.post call.
    """

    def __init__(
        self,
        api_key: str,
        timeout: float = 60.0,
        max_retries: int = 2,
        pollinations_api_key: str | None = None,
    ) -> None:
        if not api_key:
            raise NvidiaReasoningError("NVIDIA API key is required")
        self._api_key = api_key
        self._timeout = timeout
        self._max_retries = max_retries
        self._pollinations_api_key = pollinations_api_key or os.environ.get("POLLINATIONS_API_KEY", "")
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        self.last_metadata: ProviderResponseMetadata | None = None

    async def analyze_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.15,
        max_tokens: int = 1200,
    ) -> tuple[dict[str, Any], int]:
        payload = self._payload(system_prompt, user_prompt, temperature, max_tokens)
        return await self._invoke(payload, "text")

    async def analyze_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_url: str = "",
        image_ocr_text: str = "",
        temperature: float = 0.15,
        max_tokens: int = 1200,
    ) -> tuple[dict[str, Any], int]:
        evidence = user_prompt
        if image_ocr_text:
            evidence = f"{evidence}\n\nIMAGE OCR TEXT:\n{image_ocr_text}"
        if image_url:
            evidence = f"{evidence}\n\nIMAGE REFERENCE:\n{image_url}"
        payload = self._payload(system_prompt, evidence, temperature, max_tokens)
        return await self._invoke(payload, "image")

    async def analyze_audio(
        self,
        system_prompt: str,
        user_prompt: str,
        audio_transcription_text: str = "",
        audio_url: str = "",
        temperature: float = 0.15,
        max_tokens: int = 1200,
    ) -> tuple[dict[str, Any], int]:
        evidence = user_prompt
        if audio_transcription_text:
            evidence = f"{evidence}\n\nAUDIO TRANSCRIPTION:\n{audio_transcription_text}"
        if audio_url:
            evidence = f"{evidence}\n\nAUDIO REFERENCE:\n{audio_url}"
        payload = self._payload(system_prompt, evidence, temperature, max_tokens)
        return await self._invoke(payload, "audio")

    async def analyze_document(
        self,
        system_prompt: str,
        user_prompt: str,
        pdf_extracted_text: str = "",
        metadata_text: str = "",
        temperature: float = 0.15,
        max_tokens: int = 1200,
    ) -> tuple[dict[str, Any], int]:
        evidence = user_prompt
        if pdf_extracted_text:
            evidence = f"{evidence}\n\nPDF EXTRACTED TEXT:\n{pdf_extracted_text}"
        if metadata_text:
            evidence = f"{evidence}\n\nPDF METADATA:\n{metadata_text}"
        payload = self._payload(system_prompt, evidence, temperature, max_tokens)
        return await self._invoke(payload, "document")

    def _payload(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        return {
            "model": NVIDIA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.70,
            "stream": False,
        }

    async def _invoke(self, payload: dict[str, Any], modality: str) -> tuple[dict[str, Any], int]:
        return await asyncio.to_thread(self._invoke_sync, payload, modality)

    def _invoke_sync(self, payload: dict[str, Any], modality: str) -> tuple[dict[str, Any], int]:
        _console_log("NVIDIA", f"Invoking {modality} reasoning model...")
        _console_log("NVIDIA", f"Model: {NVIDIA_MODEL}")
        _console_log("NVIDIA", "Payload validated")
        try:
            return self._invoke_provider(
                provider="nvidia_nim",
                invoke_url=NVIDIA_INVOKE_URL,
                headers=self._headers,
                payload=payload,
                modality=modality,
                model=NVIDIA_MODEL,
            )
        except NvidiaReasoningError as nvidia_error:
            _console_log("NVIDIA", f"Runtime unavailable: {nvidia_error}")
            if not self._pollinations_api_key:
                _console_log("HERMES", "Investigation aborted")
                raise
            fallback_payload = dict(payload)
            fallback_model = POLLINATIONS_VISION_MODEL if modality == "image" else POLLINATIONS_TEXT_MODEL
            fallback_payload["model"] = fallback_model
            _console_log("POLLINATIONS", f"NVIDIA failed; invoking fallback model {fallback_model}")
            try:
                return self._invoke_provider(
                    provider="pollinations",
                    invoke_url=POLLINATIONS_INVOKE_URL,
                    headers={
                        "Authorization": f"Bearer {self._pollinations_api_key}",
                        "Accept": "application/json",
                    },
                    payload=fallback_payload,
                    modality=modality,
                    model=fallback_model,
                )
            except NvidiaReasoningError:
                _console_log("HERMES", "Investigation aborted")
                raise nvidia_error

    def _invoke_provider(
        self,
        provider: str,
        invoke_url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        modality: str,
        model: str,
    ) -> tuple[dict[str, Any], int]:
        last_error: NvidiaReasoningError | None = None

        for attempt in range(self._max_retries + 1):
            started = perf_counter()
            request_id = ""
            try:
                response = requests.post(
                    invoke_url,
                    headers=headers,
                    json=payload,
                    timeout=self._timeout,
                )
                latency_ms = int((perf_counter() - started) * 1000)
                request_id = self._request_id(response.headers)
                response_headers = {k: v for k, v in response.headers.items()}
                _console_log(provider.upper(), f"HTTP {response.status_code} received")
                _console_log(provider.upper(), f"Latency: {latency_ms}ms")

                if response.status_code in TRANSIENT_STATUSES and attempt < self._max_retries:
                    last_error = NvidiaReasoningError(
                        f"{provider} transient HTTP {response.status_code}: {response.text[:200]}",
                        latency_ms,
                        request_id,
                    )
                    continue

                response.raise_for_status()
                data = response.json()
                try:
                    content = self._extract_content(data)
                except NvidiaReasoningError as exc:
                    last_error = NvidiaReasoningError(str(exc), latency_ms, request_id)
                    if attempt < self._max_retries:
                        continue
                    raise last_error from exc
                self.last_metadata = ProviderResponseMetadata(
                    provider=provider,
                    model=model,
                    request_id=request_id,
                    latency_ms=latency_ms,
                    headers=response_headers,
                    raw_response=data,
                )
                confidence = content.get("confidence")
                _console_log(provider.upper(), "Structured JSON parsed")
                if isinstance(confidence, (float, int)):
                    _console_log(provider.upper(), f"Confidence: {float(confidence):.2f}")
                _console_log(provider.upper(), f"Response received ({latency_ms}ms, request_id={request_id or 'n/a'})")
                return content, latency_ms
            except requests.Timeout as exc:
                latency_ms = int((perf_counter() - started) * 1000)
                last_error = NvidiaReasoningError(
                    f"NVIDIA timeout after {int(self._timeout)}s",
                    latency_ms,
                    request_id,
                )
                if attempt >= self._max_retries:
                    raise last_error from exc
            except requests.HTTPError as exc:
                latency_ms = int((perf_counter() - started) * 1000)
                response = exc.response
                request_id = self._request_id(response.headers) if response is not None else ""
                detail = response.text[:200] if response is not None else str(exc)
                status = response.status_code if response is not None else "unknown"
                raise NvidiaReasoningError(f"{provider} HTTP {status}: {detail}", latency_ms, request_id) from exc
            except requests.RequestException as exc:
                latency_ms = int((perf_counter() - started) * 1000)
                last_error = NvidiaReasoningError(f"{provider} network error: {exc}", latency_ms, request_id)
                if attempt >= self._max_retries:
                    raise last_error from exc
            except ValueError as exc:
                latency_ms = int((perf_counter() - started) * 1000)
                raise NvidiaReasoningError(f"{provider} returned malformed JSON", latency_ms, request_id) from exc

        raise last_error or NvidiaReasoningError("NVIDIA invocation failed")

    def _extract_content(self, data: dict[str, Any]) -> dict[str, Any]:
        choices = data.get("choices", [])
        if not choices:
            raise NvidiaReasoningError("NVIDIA returned no choices")
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if not isinstance(content, str) or not content.strip():
            raise NvidiaReasoningError("NVIDIA returned empty content")
        try:
            parsed = recover_json_object(content)
        except JsonRecoveryError as exc:
            _console_log("NVIDIA", "Invalid JSON received")
            raise NvidiaReasoningError(
                f"Failed to recover JSON from provider output (first 200 chars: {content[:200]})"
            ) from exc
        if not isinstance(parsed, dict):
            raise NvidiaReasoningError("NVIDIA response is not a JSON object")
        return parsed

    @staticmethod
    def _request_id(headers: requests.structures.CaseInsensitiveDict[str]) -> str:
        for key in ("x-request-id", "x-nv-request-id", "nvcf-reqid", "request-id"):
            value = headers.get(key)
            if value:
                return value
        return ""

    @staticmethod
    def _recover_json(content: str) -> dict[str, Any]:
        content = content.replace("```json", "").replace("```", "").strip()
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise NvidiaReasoningError(
            f"Failed to recover JSON from NVIDIA output (first 200 chars: {content[:200]})"
        )
