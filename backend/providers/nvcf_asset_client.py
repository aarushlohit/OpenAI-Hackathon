"""
NVIDIA Cloud Functions (NVCF) Asset API client.

Handles the two-step pre-signed S3 upload workflow required for large payloads
(images typically >180 KB base64) before calling NIM inference endpoints.

Workflow:
  1. POST /v2/nvcf/assets  → receive assetId + uploadUrl (S3 presigned)
  2. PUT  <uploadUrl>       → stream raw binary bytes
  3. Return assetId for use in NVCF-INPUT-ASSET-REFERENCES header
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVCF_ASSETS_URL = "https://api.nvcf.nvidia.com/v2/nvcf/assets"

# Threshold in bytes for base64-encoded payload (~180 KB base64 ≈ 135 KB raw)
# We compare raw bytes against a generous threshold so borderline files always
# go through the asset API rather than risk a 413 from the inference endpoint.
ASSET_THRESHOLD_BYTES = int(os.getenv("NVCF_ASSET_THRESHOLD_BYTES", str(130_000)))


def should_use_asset_api(image_bytes: bytes) -> bool:
    """Return True when the raw image exceeds the safe inline threshold."""
    return len(image_bytes) > ASSET_THRESHOLD_BYTES


def upload_asset(image_bytes: bytes, content_type: str, description: str = "NIM inference input") -> str:
    """
    Upload *image_bytes* via the NVCF Asset API and return the assetId.

    Raises RuntimeError on any network or API failure.
    """
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not set — cannot call NVCF Asset API")

    # ── Step 1: request a presigned upload URL ──────────────────────────────
    init_headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    init_payload = {
        "contentType": content_type,
        "description": description,
    }

    try:
        init_resp = requests.post(
            NVCF_ASSETS_URL,
            headers=init_headers,
            json=init_payload,
            timeout=30,
        )
        init_resp.raise_for_status()
        init_data = init_resp.json()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"NVCF Asset API init failed HTTP {exc.response.status_code}: "
            f"{exc.response.text[:400]}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"NVCF Asset API init request failed: {exc}") from exc

    asset_id: str = init_data.get("assetId", "")
    upload_url: str = init_data.get("uploadUrl", "")

    if not asset_id or not upload_url:
        raise RuntimeError(f"NVCF Asset API returned unexpected response: {init_data}")

    # ── Step 2: PUT raw binary to the presigned S3 URL ─────────────────────
    put_headers = {"Content-Type": content_type}

    try:
        put_resp = requests.put(
            upload_url,
            data=image_bytes,
            headers=put_headers,
            timeout=120,
        )
        put_resp.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"NVCF S3 upload failed HTTP {exc.response.status_code}: "
            f"{exc.response.text[:400]}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"NVCF S3 upload request failed: {exc}") from exc

    return asset_id
