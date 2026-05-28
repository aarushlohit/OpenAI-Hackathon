#!/usr/bin/env python3
"""Live real-runtime validation for Hermes-X.

This script validates actual provider/OCR/orchestrator/event/replay/graph/API behavior.
It does not synthesize mock verdicts.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.container import AppContainer
from app.providers.nvidia_reasoning_client import NVIDIA_MODEL, NvidiaReasoningClient
from app.schemas.investigation import InvestigationInputKind, InvestigationRequest
from app.security.model_output_validator import ModelOutputValidator
from app.services.ocr import SafeOCRService

TEXT_TEST = (
    "Telegram HR from @careerfastjob asks refundable onboarding payment of 3500 via UPI pay@upi "
    "and asks onboarding through Telegram only."
)


async def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    checks.append(await _check_nvidia())
    checks.append(await _check_ocr())
    checks.append(await _check_text_pipeline())
    checks.append(await _check_image_pipeline())
    checks.append(await _check_websocket_replay_graph())
    checks.append(_check_gui_api_compatibility())

    print("\nLIVE REAL VALIDATION SUMMARY")
    print("=" * 60)
    ok = True
    for name, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'}: {name} - {detail}")
        ok = ok and passed
    return 0 if ok else 1


async def _check_nvidia() -> tuple[str, bool, str]:
    api_key = _load_key("NVIDIA_NIM_API_KEY") or _load_key("NVIDIA_API_KEY")
    if not api_key:
        return ("nvidia_connectivity", False, "NVIDIA key missing")
    client = NvidiaReasoningClient(api_key=api_key, timeout=60)
    last_error = ""
    for _ in range(3):
        try:
            output, latency = await client.analyze_text(
                "Return minified JSON only. Do not explain. Analyze recruitment fraud risk. Use exactly one strongest signal.",
                (
                    f"EVIDENCE:\n{TEXT_TEST}\n\n"
                    '{"risk_score":0-100,"risk_level":"LOW|MEDIUM|HIGH|CRITICAL",'
                    '"confidence":0.0-1.0,"signals":[{"name":"...",'
                    '"severity":"LOW|MEDIUM|HIGH|CRITICAL","confidence":0.0-1.0,'
                    '"source":"ai_reasoned","explanation":"max 40 chars"}],"summary":"max 80 chars",'
                    '"recommended_action":"...","reasoning_type":"behavioral_analysis"}'
                ),
            )
            ModelOutputValidator().validate_behavior_output(output)
            request_id = client.last_metadata.request_id if client.last_metadata else "N/A"
            return ("nvidia_connectivity", True, f"{NVIDIA_MODEL}, request_id={request_id}, latency={latency}ms")
        except Exception as exc:
            last_error = str(exc)
    return ("nvidia_connectivity", False, last_error)


async def _check_ocr() -> tuple[str, bool, str]:
    try:
        from PIL import Image, ImageDraw

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "telegram_onboarding.png"
            image = Image.new("RGB", (1000, 260), "white")
            draw = ImageDraw.Draw(image)
            draw.text((20, 40), "Telegram HR asks onboarding payment 3500 UPI pay@upi", fill="black")
            image.save(path)
            result = await SafeOCRService().extract(str(path))
        visible = result.extracted_text.strip()
        if not visible:
            return ("ocr", False, "OCR produced no text")
        return ("ocr", True, visible[:120])
    except Exception as exc:
        return ("ocr", False, str(exc))


async def _check_text_pipeline() -> tuple[str, bool, str]:
    try:
        container = AppContainer()
        request = InvestigationRequest(raw_input=TEXT_TEST, kind=InvestigationInputKind.TEXT)
        result = await container.orchestrator.investigate(request)
        provider = result.active_provider or "none"
        if provider not in {"nvidia_nim", "pollinations", "openai"}:
            return ("text_pipeline", False, f"no real provider attribution: {provider}")
        if result.finding.risk_level.value not in {"high", "critical"}:
            return ("text_pipeline", False, f"expected HIGH/CRITICAL, got {result.finding.risk_level.value}")
        return ("text_pipeline", True, f"{result.finding.risk_level.value}, provider={provider}")
    except Exception as exc:
        return ("text_pipeline", False, str(exc))


async def _check_image_pipeline() -> tuple[str, bool, str]:
    try:
        from PIL import Image, ImageDraw

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "telegram_onboarding.png"
            image = Image.new("RGB", (1000, 260), "white")
            draw = ImageDraw.Draw(image)
            draw.text((20, 40), "Telegram HR asks onboarding payment 3500 UPI pay@upi", fill="black")
            image.save(path)
            container = AppContainer()
            request = InvestigationRequest(raw_input=str(path), kind=InvestigationInputKind.IMAGE_REFERENCE)
            result = await container.orchestrator.investigate(request)
        provider = result.active_provider or "none"
        if provider not in {"nvidia_nim", "pollinations", "openai"}:
            return ("image_pipeline", False, f"no real provider attribution: {provider}")
        return ("image_pipeline", True, f"{result.finding.risk_level.value}, provider={provider}")
    except Exception as exc:
        return ("image_pipeline", False, str(exc))


async def _check_websocket_replay_graph() -> tuple[str, bool, str]:
    try:
        container = AppContainer()
        request = InvestigationRequest(raw_input=TEXT_TEST, kind=InvestigationInputKind.TEXT)
        result = await container.orchestrator.investigate(request)
        events = await container.investigation_repository.list_events(result.investigation_id)
        replay = await container.replay_engine.build(result.investigation_id)
        replay_ok = container.replay_engine.verify(replay)
        graph_metrics = container.graph_metrics.snapshot()
        if not events:
            return ("websocket_replay_graph", False, "no persisted events")
        if not replay_ok:
            return ("websocket_replay_graph", False, "replay verification failed")
        return (
            "websocket_replay_graph",
            True,
            f"events={len(events)}, graph_nodes={graph_metrics.get('nodes_projected', 0)}",
        )
    except Exception as exc:
        return ("websocket_replay_graph", False, str(exc))


def _check_gui_api_compatibility() -> tuple[str, bool, str]:
    try:
        from app.api.server import create_app

        app = create_app()
        paths = {route.path for route in app.routes}
        required = {"/v1/investigate", "/v1/investigate/upload", "/v1/ws/investigations/{correlation_id}"}
        missing = sorted(required - paths)
        if missing:
            return ("gui_api_compatibility", False, f"missing routes: {missing}")
        return ("gui_api_compatibility", True, "required REST/WebSocket routes registered")
    except Exception as exc:
        return ("gui_api_compatibility", False, str(exc))


def _load_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    for path in (Path(".env"), Path("app/.env")):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, raw = line.split("=", 1)
            if key.strip() == name:
                return raw.strip().strip('"').strip("'")
    return ""


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
