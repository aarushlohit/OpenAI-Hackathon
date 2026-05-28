#!/usr/bin/env python3
"""Provider-first NVIDIA cognition proof.

This script intentionally ignores orchestration, agents, replay, websocket, graph,
and Flutter. It proves only that real NVIDIA cognition works.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

import requests

INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
DEFAULT_TEXT = (
    "I got offer letter from google to confirm onboarding pay 25k one time to "
    "onboard.googles.xyz"
)

SYSTEM_PROMPT = (
    "Return minified JSON only. Do not explain. Do not reason in prose. "
    "Analyze recruitment fraud risk. Use exactly one strongest signal."
)


class FailClosed(RuntimeError):
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Direct NVIDIA cognition test.")
    parser.add_argument(
        "mode",
        nargs="?",
        default="text",
        choices=("text", "image", "pdf", "audio"),
        help="Evidence mode to test.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=DEFAULT_TEXT,
        help="Text input or artifact path.",
    )
    args = parser.parse_args()

    try:
        api_key = _load_api_key()
        user_input = _prepare_user_input(args.mode, args.input)
        data, headers, latency_ms = _invoke_nvidia(api_key, user_input)
        structured = _extract_structured_json(data)
        print("\nMODEL NAME:")
        print(MODEL)
        print("\nREQUEST ID:")
        print(_request_id(headers) or "N/A")
        print("\nLATENCY MS:")
        print(latency_ms)
        print("\nSTRUCTURED JSON:")
        print(json.dumps(structured, indent=2))
        return 0
    except FailClosed as exc:
        print("\nNVIDIA runtime unavailable.")
        print("Investigation aborted.")
        print(f"Reason: {exc}")
        return 1


def _load_api_key() -> str:
    value = os.environ.get("NVIDIA_NIM_API_KEY") or os.environ.get("NVIDIA_API_KEY")
    if value:
        return value
    for path in (Path(".env"), Path("app/.env")):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, raw = line.split("=", 1)
            if key.strip() in {"NVIDIA_NIM_API_KEY", "NVIDIA_API_KEY"}:
                value = raw.strip().strip('"').strip("'")
                if value:
                    return value
    raise FailClosed("NVIDIA_NIM_API_KEY is not set")


def _prepare_user_input(mode: str, raw_input: str) -> str:
    if mode == "text":
        return _prompt_for("text", raw_input)
    path = Path(raw_input).expanduser()
    if not path.exists():
        raise FailClosed(f"{mode} artifact not found: {path}")
    if mode == "image":
        ocr_text = _extract_image_text(path)
        print("\nOCR TEXT:")
        print(ocr_text)
        return _prompt_for("image_ocr", f"IMAGE_PATH: {path}\nOCR_TEXT:\n{ocr_text}")
    if mode == "pdf":
        extracted_text = _extract_pdf_text(path)
        print("\nPDF EXTRACTED TEXT:")
        print(extracted_text)
        return _prompt_for("pdf_document", f"PDF_PATH: {path}\nEXTRACTED_TEXT:\n{extracted_text}")
    if mode == "audio":
        transcription = _transcribe_audio(path)
        print("\nAUDIO TRANSCRIPTION:")
        print(transcription)
        return _prompt_for("audio_transcription", f"AUDIO_PATH: {path}\nTRANSCRIPTION:\n{transcription}")
    raise FailClosed(f"Unsupported mode: {mode}")


def _prompt_for(reasoning_type: str, evidence: str) -> str:
    return (
        f"MODE: {reasoning_type}\n"
        f"EVIDENCE:\n{evidence}\n\n"
        "Return only this JSON object with real values: "
        '{"risk_score":0-100,"risk_level":"LOW|MEDIUM|HIGH|CRITICAL",'
        '"confidence":0.0-1.0,"signals":[{"name":"...",'
        '"severity":"LOW|MEDIUM|HIGH|CRITICAL","confidence":0.0-1.0,'
        '"explanation":"max 40 chars","source":"ai_reasoned"}],"summary":"max 80 chars",'
        '"recommended_action":"max 60 chars","reasoning_type":"'
        f'{reasoning_type}"' + "}"
    )


def _invoke_nvidia(api_key: str, user_input: str) -> tuple[dict[str, Any], dict[str, str], int]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
        "max_tokens": 1200,
        "temperature": 0.15,
        "top_p": 0.70,
        "stream": False,
    }

    print("\nRAW PAYLOAD:")
    print(json.dumps(payload, indent=2))

    started = perf_counter()
    try:
        response = requests.post(
            INVOKE_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise FailClosed(f"NVIDIA request failed: {exc}") from exc
    latency_ms = int((perf_counter() - started) * 1000)

    try:
        data = response.json()
    except ValueError as exc:
        raise FailClosed(f"NVIDIA returned non-JSON HTTP {response.status_code}: {response.text[:500]}") from exc

    print("\nRAW RESPONSE:")
    print(json.dumps(data, indent=2))

    if response.status_code >= 400:
        raise FailClosed(f"NVIDIA HTTP {response.status_code}")
    return data, dict(response.headers), latency_ms


def _extract_structured_json(data: dict[str, Any]) -> dict[str, Any]:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise FailClosed("NVIDIA response has no choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise FailClosed("NVIDIA response has no message")
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise FailClosed("NVIDIA response content is empty")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise FailClosed(f"NVIDIA content was not strict JSON: {content[:500]}") from exc
    if not isinstance(parsed, dict):
        raise FailClosed("NVIDIA content JSON is not an object")
    return parsed


def _extract_image_text(path: Path) -> str:
    try:
        from PIL import Image
        import pytesseract
    except ImportError as exc:
        raise FailClosed("Image OCR requires installed PIL and pytesseract") from exc
    text = pytesseract.image_to_string(Image.open(path)).strip()
    if not text:
        raise FailClosed("OCR produced no text")
    return text


def _extract_pdf_text(path: Path) -> str:
    errors: list[str] = []
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if text:
            return text[:20000]
        errors.append("pypdf produced no text")
    except ImportError as exc:
        errors.append(f"pypdf unavailable: {exc}")
    except Exception as exc:
        errors.append(f"pypdf failed: {exc}")

    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if text:
            return text[:20000]
        errors.append("PyPDF2 produced no text")
    except ImportError as exc:
        errors.append(f"PyPDF2 unavailable: {exc}")
    except Exception as exc:
        errors.append(f"PyPDF2 failed: {exc}")

    raise FailClosed("; ".join(errors) or "PDF extraction failed")


def _transcribe_audio(path: Path) -> str:
    whisper_cmd = _find_command("whisper")
    if whisper_cmd:
        proc = subprocess.run(
            [
                whisper_cmd,
                str(path),
                "--model",
                "base",
                "--output_format",
                "txt",
                "--output_dir",
                str(path.parent),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=300,
        )
        txt_path = path.with_suffix(".txt")
        if proc.returncode == 0 and txt_path.exists():
            text = txt_path.read_text(encoding="utf-8").strip()
            if text:
                return text[:20000]
        raise FailClosed(f"whisper transcription failed: {(proc.stderr or proc.stdout)[:500]}")

    raise FailClosed("Audio transcription requires a real local whisper CLI; no fake transcription used")


def _find_command(name: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _request_id(headers: dict[str, str]) -> str:
    lowered = {key.lower(): value for key, value in headers.items()}
    for key in ("x-request-id", "x-nv-request-id", "nvcf-reqid", "request-id"):
        value = lowered.get(key)
        if value:
            return value
    return ""


if __name__ == "__main__":
    raise SystemExit(main())
