"""
NVIDIA NIM text reasoning client.
Real requests.post only — no mocks, no fallback, fail-closed.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_TEXT_MODEL = os.getenv("NVIDIA_TEXT_MODEL", "google/gemma-3n-e2b-it")

INVOKE_URL = f"{NVIDIA_BASE_URL}/chat/completions"


def reason(messages: list[dict], max_tokens: int = 1024, temperature: float = 0.20) -> str:
    """
    Send messages to NVIDIA NIM and return the assistant content string.
    Raises RuntimeError if the provider fails (fail-closed).
    """
    if not NVIDIA_API_KEY:
        raise RuntimeError("NVIDIA_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "model": NVIDIA_TEXT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.70,
        "stream": False,
    }

    try:
        resp = requests.post(INVOKE_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content
    except requests.HTTPError as e:
        raise RuntimeError(f"NVIDIA NIM HTTP error {e.response.status_code}: {e.response.text[:300]}") from e
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"NVIDIA NIM unexpected response structure: {e}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"NVIDIA NIM request failed: {e}") from e


def model_name() -> str:
    return NVIDIA_TEXT_MODEL
