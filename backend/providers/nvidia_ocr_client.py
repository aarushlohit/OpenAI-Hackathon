"""
NVIDIA Nemotron OCR client.

Uses the nvidia/nemotron-ocr-v1 NIM endpoint to extract text from images.

Large images (raw bytes > NVCF_ASSET_THRESHOLD_BYTES) are uploaded via the
NVCF Asset API (pre-signed S3) before the inference call, as required by the
NVIDIA API Catalog for payloads exceeding the inline base64 limit (~180 KB).

Small images are sent inline as base64 data-URLs — identical to the snippet
shown in the NVIDIA NIM documentation.
"""

import os
import base64
import json
import requests
from dotenv import load_dotenv

try:
    from providers.nvcf_asset_client import should_use_asset_api, upload_asset
except ModuleNotFoundError:
    from backend.providers.nvcf_asset_client import should_use_asset_api, upload_asset

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
OCR_INVOKE_URL = os.getenv(
    "NVIDIA_OCR_URL",
    "https://ai.api.nvidia.com/v1/cv/nvidia/nemotron-ocr-v1",
)


def ocr_image(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """
    Run OCR on *image_bytes* using NVIDIA Nemotron OCR.

    Automatically routes through the NVCF Asset API when the image exceeds the
    inline payload threshold.  Returns extracted text as a string.

    Raises RuntimeError on any provider failure.
    """
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not set — cannot call Nemotron OCR")

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if should_use_asset_api(image_bytes):
        # ── Large image: upload via NVCF Asset API ──────────────────────────
        asset_id = upload_asset(
            image_bytes,
            content_type=mime_type,
            description="OCR page image for Hermes-X",
        )
        headers["NVCF-INPUT-ASSET-REFERENCES"] = asset_id
        # Reference the uploaded asset inside the payload using the NVCF format
        img_src = f"data:{mime_type};asset_id,{asset_id}"
        payload = {
            "input": [
                {
                    "type": "image_url",
                    "url": img_src,
                }
            ]
        }
    else:
        # ── Small image: inline base64 ──────────────────────────────────────
        b64 = base64.b64encode(image_bytes).decode()
        payload = {
            "input": [
                {
                    "type": "image_url",
                    "url": f"data:{mime_type};base64,{b64}",
                }
            ]
        }

    try:
        resp = requests.post(OCR_INVOKE_URL, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Nemotron OCR HTTP {exc.response.status_code}: {exc.response.text[:400]}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Nemotron OCR request failed: {exc}") from exc

    # Response schema: {"data": [{"text_detections": [{"text_prediction": {"text": "..."}}]}]} or {"text": "..."} or choices[]-style
    if "data" in data and isinstance(data["data"], list):
        extracted_texts = []
        for item in data["data"]:
            if "text_detections" in item and isinstance(item["text_detections"], list):
                for detection in item["text_detections"]:
                    pred = detection.get("text_prediction")
                    if isinstance(pred, dict) and "text" in pred:
                        extracted_texts.append(pred["text"])
        if extracted_texts:
            return "\n".join(extracted_texts)

    if "text" in data:
        return data["text"]
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    # Fallback: return raw JSON for debugging
    return json.dumps(data)


def model_name() -> str:
    return "nvidia/nemotron-ocr-v1"
