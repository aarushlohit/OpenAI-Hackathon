"""
Pollinations.ai vision reasoning client.
Sends images as base64 image_url blocks — no OCR.
"""

import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")
POLLINATIONS_CHAT_URL = os.getenv("POLLINATIONS_CHAT_URL", "https://gen.pollinations.ai/v1/chat/completions")
POLLINATIONS_VISION_MODEL = os.getenv("POLLINATIONS_VISION_MODEL", "openai-large")


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


def model_name() -> str:
    return POLLINATIONS_VISION_MODEL
