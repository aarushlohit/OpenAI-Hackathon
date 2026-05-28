"""Pollinations.ai media upload and vision reasoning client."""

import os
import base64
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

try:
    from utils.json_recovery import recover_json
except ModuleNotFoundError:
    from backend.utils.json_recovery import recover_json

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")
POLLINATIONS_CHAT_URL = os.getenv("POLLINATIONS_CHAT_URL", "https://gen.pollinations.ai/v1/chat/completions")
POLLINATIONS_IMAGE_MODEL = os.getenv("POLLINATIONS_IMAGE_MODEL", "flux")
_RAW_POLLINATIONS_VISION_MODEL = os.getenv("POLLINATIONS_VISION_MODEL", "qwen-vision")
_IMAGE_ONLY_MODELS = {
    "flux",
    "kontext",
    "nanobanana",
    "nanobanana-2",
    "nanobanana-pro",
    "seedream5",
    "seedream",
    "seedream-pro",
    "gptimage",
    "gptimage-large",
    "gpt-image-2",
    "zimage",
    "wan-image",
    "wan-image-pro",
    "qwen-image",
    "grok-imagine",
    "grok-imagine-pro",
    "klein",
    "p-image",
    "p-image-edit",
    "nova-canvas",
}
POLLINATIONS_VISION_MODEL = (
    "qwen-vision"
    if _RAW_POLLINATIONS_VISION_MODEL in _IMAGE_ONLY_MODELS
    else _RAW_POLLINATIONS_VISION_MODEL
)
POLLINATIONS_MEDIA_UPLOAD_URL = os.getenv(
    "POLLINATIONS_MEDIA_UPLOAD_URL",
    "https://media.pollinations.ai/upload",
)


def analyze_image(image_bytes: bytes, prompt: str, mime_type: str = "image/jpeg") -> str:
    """
    Analyze an image with Pollinations vision model.
    Returns the assistant content string.
    Raises RuntimeError on failure.
    """
    if not POLLINATIONS_API_KEY:
        raise RuntimeError("POLLINATIONS_API_KEY is not set")

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]

    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": POLLINATIONS_VISION_MODEL,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.2,
    }

    try:
        resp = requests.post(POLLINATIONS_CHAT_URL, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except requests.HTTPError as e:
        raise RuntimeError(f"Pollinations HTTP error {e.response.status_code}: {e.response.text[:300]}") from e
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Pollinations unexpected response structure: {e}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"Pollinations request failed: {e}") from e


def upload_image(image_bytes: bytes, filename: str, mime_type: str = "image/jpeg") -> str:
    """Upload evidence to Pollinations media storage and return the public media URL."""
    if not POLLINATIONS_API_KEY:
        raise RuntimeError("POLLINATIONS_API_KEY is not set")

    headers = {"Authorization": f"Bearer {POLLINATIONS_API_KEY}"}
    files = {"file": (filename, image_bytes, mime_type)}

    try:
        resp = requests.post(POLLINATIONS_MEDIA_UPLOAD_URL, headers=headers, files=files, timeout=60)
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as e:
        raise RuntimeError(f"Pollinations upload HTTP error {e.response.status_code}: {e.response.text[:300]}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"Pollinations upload failed: {e}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError("Pollinations upload returned non-JSON response") from e

    for key in ("url", "mediaUrl", "media_url", "publicUrl", "public_url"):
        value = data.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value

    hash_value = data.get("hash") or data.get("id")
    if isinstance(hash_value, str) and hash_value:
        return f"https://media.pollinations.ai/{hash_value}"

    raise RuntimeError(f"Pollinations upload response did not include a media URL: {data}")


def extract_offer_letter(image_bytes: bytes, filename: str, mime_type: str = "image/jpeg") -> dict:
    """
    Upload and analyze an offer-letter/recruitment image.

    Note: flux is an image generation model, so it is kept as the configured image model
    for Pollinations metadata. OCR and reasoning are performed by the vision chat model.
    """
    media_url = None
    image_reference = None
    upload_error = None

    try:
        media_url = upload_image(image_bytes, filename, mime_type)
        image_reference = media_url
    except RuntimeError as e:
        upload_error = str(e)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_reference = f"data:{mime_type};base64,{b64}"

    prompt = """Extract and assess this recruitment or offer-letter image.

Return ONLY a valid JSON object:
{
  "company_name": "company shown or Unknown",
  "document_type": "offer_letter | recruiter_chat | onboarding_form | payment_request | unknown",
  "extracted_text": "all readable text, preserving names, emails, URLs, amounts, dates, and instructions",
  "offer_summary": "short summary of what the document claims",
  "scam_conclusion": "SCAM | NOT SCAM | UNCERTAIN",
  "risk_score": 0,
  "red_flags": ["specific red flag"],
  "safe_signals": ["specific legitimate signal"],
  "reasoning": "brief evidence-based explanation"
}

Focus on company identity, offer terms, payment/deposit requests, suspicious domains,
Telegram/WhatsApp-only onboarding, unrealistic salary, urgency, and mismatched branding."""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_reference}},
            ],
        }
    ]

    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": POLLINATIONS_VISION_MODEL,
        "messages": messages,
        "max_tokens": 1400,
        "temperature": 0.1,
    }

    try:
        resp = requests.post(POLLINATIONS_CHAT_URL, headers=headers, json=payload, timeout=90)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
    except requests.HTTPError as e:
        raise RuntimeError(f"Pollinations vision HTTP error {e.response.status_code}: {e.response.text[:300]}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"Pollinations vision request failed: {e}") from e
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Pollinations vision unexpected response structure: {e}") from e

    parsed = recover_json(raw) or {"raw_response": raw}
    parsed["provider"] = f"pollinations/{POLLINATIONS_VISION_MODEL}"
    parsed["pollinations_image_model"] = POLLINATIONS_IMAGE_MODEL
    if _RAW_POLLINATIONS_VISION_MODEL != POLLINATIONS_VISION_MODEL:
        parsed["vision_model_warning"] = (
            f"{_RAW_POLLINATIONS_VISION_MODEL} is an image generation model; "
            f"used {POLLINATIONS_VISION_MODEL} for OCR/vision extraction"
        )
    parsed["media_url"] = media_url
    if upload_error:
        parsed["upload_warning"] = upload_error
    return parsed


def load_image_from_path(image_path: str) -> tuple[bytes, str, str]:
    """Read a local image path supplied from the website."""
    path = Path(image_path).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise RuntimeError(f"Image path not found: {path}")

    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    mime_type = mime_map.get(path.suffix.lower())
    if not mime_type:
        raise RuntimeError("Image path must end with .png, .jpg, .jpeg, .webp, or .gif")

    max_bytes = int(os.getenv("HERMES_MAX_IMAGE_BYTES", str(15 * 1024 * 1024)))
    if path.stat().st_size > max_bytes:
        raise RuntimeError(f"Image is too large; max size is {max_bytes // (1024 * 1024)}MB")

    return path.read_bytes(), path.name, mime_type


def model_name() -> str:
    return POLLINATIONS_VISION_MODEL
