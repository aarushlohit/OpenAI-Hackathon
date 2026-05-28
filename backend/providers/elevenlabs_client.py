"""
ElevenLabs Speech-to-Text client wrapper.
Interfaces with ElevenLabs Scribe v2 REST API to transcribe audio.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVEN_LABS_API_KEY", "")
ELEVENLABS_S2T_URL = os.getenv("ELEVENLABS_S2T_URL", "https://api.elevenlabs.io/v1/speech-to-text")
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "scribe_v2")


def transcribe_audio(audio_bytes: bytes, filename: str, mime_type: str) -> str:
    """
    Transcribe an audio file using ElevenLabs Scribe v2 API.
    Returns the transcription text string.
    Raises RuntimeError on failure.
    """
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY is not configured in the environment variables.")

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    files = {
        "file": (filename, audio_bytes, mime_type),
    }

    data = {
        "model_id": ELEVENLABS_MODEL,
    }

    try:
        # Increase timeout as transcribing larger audio files might take time
        resp = requests.post(
            ELEVENLABS_S2T_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )
        resp.raise_for_status()
        res_json = resp.json()
        
        transcript = res_json.get("text", "")
        if not transcript.strip():
            raise RuntimeError("Audio transcription completed but returned empty text.")
            
        return transcript.strip()

    except requests.HTTPError as e:
        error_msg = f"HTTP Error {resp.status_code}"
        try:
            err_json = resp.json()
            if "detail" in err_json:
                error_msg += f": {err_json['detail']}"
        except Exception:
            error_msg += f": {resp.text[:300]}"
        raise RuntimeError(f"ElevenLabs STT failed: {error_msg}") from e
    except requests.RequestException as e:
        raise RuntimeError(f"ElevenLabs request failed: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error during transcription: {e}") from e


def model_name() -> str:
    return ELEVENLABS_MODEL
