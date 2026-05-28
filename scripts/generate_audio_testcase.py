#!/usr/bin/env python3
"""
Generate audio testcase MP3 files using ElevenLabs Text-to-Speech API.
These files are placed in test_assets/audio/ for multimodal AI agent testing.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load env variables from root and backend
ROOT_DIR = Path(__file__).parents[1]
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / "backend" / ".env")

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

SCAM_TEXT = "You need to send 3000 rupees immediately to confirm your onboarding. This is urgent. We need it within 2 hours."
SAFE_TEXT = "Hi there, this is Sarah from Google Recruiting. I am pleased to inform you that your interviews went very well, and we would like to extend an offer. We will send the official documents to your email, and there are absolutely no fees or payments required at any stage of our onboarding process."

def generate_mp3(text: str, voice_id: str, output_path: Path):
    if not ELEVENLABS_API_KEY:
        print("Error: ELEVENLABS_API_KEY is not configured in the environment variables.")
        sys.exit(1)

    print(f"Generating audio with voice '{voice_id}' for: '{text}'")
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(tts_url, json=data, headers=headers, timeout=60)
        if response.status_code != 200:
            print(f"Error from ElevenLabs: {response.status_code} - {response.text}")
            sys.exit(1)
        
        # Ensure directories exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"Successfully generated and saved to: {output_path}")
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

def main():
    scam_dest = ROOT_DIR / "test_assets" / "audio" / "scams" / "recruiter_call_payment_request.mp3"
    safe_dest = ROOT_DIR / "test_assets" / "audio" / "legitimate" / "safe_recruiter_call.mp3"

    # Voice IDs:
    # Charlie: IKne3meq5aSn9XLyUdCD (premade)
    # Sarah: EXAVITQu4vr4xnSDxMaL (premade)
    
    print("Generating SCAM audio test case...")
    generate_mp3(SCAM_TEXT, "IKne3meq5aSn9XLyUdCD", scam_dest)

    print("\nGenerating SAFE audio test case...")
    generate_mp3(SAFE_TEXT, "EXAVITQu4vr4xnSDxMaL", safe_dest)

    print("\nDone generating audio test cases!")

if __name__ == "__main__":
    main()
