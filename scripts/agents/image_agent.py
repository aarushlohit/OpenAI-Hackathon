#!/usr/bin/env python3
"""Image agent that uses Pollinations AI for vision analysis.

Usage: python3 image_agent.py --file /path/to/image.png
"""
import os
import sys
import json
import argparse
import base64
from pathlib import Path

import requests
from openai import OpenAI  # Pollinations is OpenAI-compatible


def call_pollinations(image_path: str) -> dict:
    """Use Pollinations AI for image analysis (vision model)."""
    poll_key = os.environ.get("POLLINATIONS_API_KEY")
    if not poll_key:
        raise EnvironmentError("POLLINATIONS_API_KEY environment variable must be set")

    # Read image and encode as base64
    image_data = Path(image_path).read_bytes()
    image_b64 = base64.b64encode(image_data).decode()
    
    # Determine MIME type
    ext = Path(image_path).suffix.lower()
    mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
    mime_type = mime_map.get(ext, "image/jpeg")
    
    # Use OpenAI-compatible client for Pollinations
    client = OpenAI(
        api_key=poll_key,
        base_url="https://gen.pollinations.ai"
    )
    
    # Create vision request
    analysis_prompt = """Analyze this image for scams, phishing, forgery, or fraud indicators.
Return ONLY a JSON object with:
- is_scam: boolean
- confidence: 0-1 (confidence in assessment)
- signals: array of detected threats [{name, severity, confidence}]
- risk_score: 0-100
- explanation: brief summary

Valid severities: CRITICAL, HIGH, MEDIUM, LOW
No markdown or explanations outside JSON."""
    
    response = client.chat.completions.create(
        model="openai",  # Pollinations routes to best available vision model
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": analysis_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}
                    }
                ]
            }
        ],
        temperature=0.2,
        max_tokens=512
    )
    
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
        result["provider"] = "pollinations/vision-openai"
        return result
    except json.JSONDecodeError:
        return {
            "provider": "pollinations/vision-openai",
            "raw_response": content,
            "is_scam": False,
            "confidence": 0.5
        }


def heuristic_local(image_path: str) -> dict:
    """Fallback deterministic analysis (only when Pollinations API unavailable)."""
    name = Path(image_path).name.lower()
    if "scam" in name or "telegram" in name or "phish" in name:
        return {
            "provider": "local_heuristic_fallback",
            "is_scam": True,
            "confidence": 0.86,
            "signals": [{"name": "filename_heuristic", "severity": "MEDIUM", "confidence": 0.86}],
            "risk_score": 65
        }
    return {
        "provider": "local_heuristic_fallback",
        "is_scam": False,
        "confidence": 0.94,
        "signals": [],
        "risk_score": 10
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", help="Path to image file", required=True)
    args = p.parse_args()

    if not Path(args.file).exists():
        print(json.dumps({"error": "file not found"}))
        sys.exit(2)

    try:
        result = call_pollinations(args.file)
    except Exception as e:
        # Fallback to deterministic analysis
        result = heuristic_local(args.file)
        result["fallback_reason"] = str(e)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
