"""
NVIDIA Cloud Functions (NVCF) Asset API client.

Handles the two-step pre-signed S3 upload workflow required for large payloads
(images typically >180 KB base64) before calling NIM inference endpoints.

Workflow:
  1. POST /v2/nvcf/assets  → receive assetId + uploadUrl (S3 presigned)
  2. PUT  <uploadUrl>       → upload binary with EXACTLY the signed headers
  3. Return assetId for use in NVCF-INPUT-ASSET-REFERENCES header

IMPORTANT — AWS Signature V4 header matching:
  NVIDIA's presigned URLs sign these headers:
    content-type;host;x-amz-meta-nvcf-asset-description
  The PUT request MUST send both:
    Content-Type: <same contentType used in POST>
    x-amz-meta-nvcf-asset-description: <same description used in POST>
  Any mismatch (extra headers OR missing headers) causes HTTP 403
  SignatureDoesNotMatch.
"""

import os
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVCF_ASSETS_URL = "https://api.nvcf.nvidia.com/v2/nvcf/assets"

# Threshold in BASE64 bytes (not raw bytes). The inline limit for Nemotron OCR
# is ~200 KB of base64-encoded data. We use 195,000 bytes as a safe margin.
# Pages producing a larger base64 payload fall back to the NVCF Asset API.
ASSET_THRESHOLD_B64_BYTES = int(os.getenv("NVCF_ASSET_THRESHOLD_BYTES", str(195_000)))


def should_use_asset_api(image_bytes: bytes) -> bool:
    """Return True when the base64-encoded image exceeds the safe inline limit."""
    import base64
    return len(base64.b64encode(image_bytes)) > ASSET_THRESHOLD_B64_BYTES


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

    # ── Step 2: PUT raw binary with exactly the AWS-signed headers ──────────
    #
    # AWS Signature V4 signs a specific set of headers listed in the presigned
    # URL's X-Amz-SignedHeaders parameter. For NVIDIA's NVCF assets endpoint
    # this is always: content-type;host;x-amz-meta-nvcf-asset-description
    #
    # The PUT must include EXACTLY those headers with values that match what
    # was used when the URL was generated:
    #   • Content-Type              = same contentType sent in the init POST
    #   • x-amz-meta-nvcf-asset-description = same description sent in the init POST
    # Adding extra headers or omitting required ones → HTTP 403 SignatureDoesNotMatch.
    #
    put_headers = {
        "Content-Type": content_type,
        "x-amz-meta-nvcf-asset-description": description,
    }

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

