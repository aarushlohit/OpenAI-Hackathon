#!/usr/bin/env python3
"""Text agent that calls NVIDIA NIM API for real scam detection.

Usage: python3 text_agent.py --file /path/to/text.txt
"""
import os
import sys
import json
import argparse
from pathlib import Path

import requests


def call_nim_api(text: str) -> dict:
    """Call NVIDIA NIM API for multimodal text analysis."""
    nim_key = os.environ.get("NIM_API_KEY")
    if not nim_key:
        raise EnvironmentError("NIM_API_KEY environment variable must be set")

    # NVIDIA NIM endpoint for chat completions
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    
    # Craft prompt for scam detection
    detection_prompt = f"""Analyze this text for scams, phishing, and threats. Return a JSON object with:
- signals: array of detected threats (name, severity, confidence 0-1)
- risk_score: 0-100
- is_scam: boolean

Text: {text}

Respond ONLY with valid JSON, no markdown."""
    
    payload = {
        "model": "google/gemma-3n-e2b-it",
        "messages": [{"role": "user", "content": detection_prompt}],
        "max_tokens": 512,
        "temperature": 0.2,
        "top_p": 0.7,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {nim_key}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    
    data = resp.json()
    # Extract content from NIM response
    if "choices" in data and len(data["choices"]) > 0:
        content = data["choices"][0].get("message", {}).get("content", "{}")
        # Handle markdown-wrapped JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        try:
            result = json.loads(content)
            result["provider"] = "nvidia/gemma-3n-e2b-it"
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from the content
            return {"provider": "nvidia/gemma-3n-e2b-it", "raw_response": content}
    
    return {"error": "Invalid response from NIM", "provider": "nvidia/gemma-3n-e2b-it"}


def heuristic_local(text: str) -> dict:
    """Fallback deterministic analysis (only when NIM API unavailable)."""
    lowered = text.lower()
    signals = []
    if "send" in lowered and ("upi" in lowered or "pay" in lowered or "deposit" in lowered):
        signals.append({"name": "payment_coercion", "severity": "CRITICAL", "confidence": 0.95})
    if "telegram" in lowered or "whatsapp" in lowered:
        signals.append({"name": "channel_restriction", "severity": "HIGH", "confidence": 0.88})
    if "urgent" in lowered or "immediately" in lowered or "within 24" in lowered:
        signals.append({"name": "urgency_pressure", "severity": "HIGH", "confidence": 0.82})

    risk = sum(25 if s["severity"] == "CRITICAL" else 18 for s in signals) or 10
    confidence = sum(s["confidence"] for s in signals) / len(signals) if signals else 0.95
    return {
        "provider": "local_heuristic_fallback",
        "signals": signals,
        "risk_score": risk,
        "confidence": confidence,
        "severity": "HIGH" if risk >= 50 else "MEDIUM" if risk >= 25 else "LOW"
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", help="Path to text file", default=None)
    args = p.parse_args()

    if args.file:
        text = Path(args.file).read_text()
    else:
        text = sys.stdin.read()

    try:
        result = call_nim_api(text)
    except Exception as e:
        # Fallback to deterministic analysis
        result = heuristic_local(text)
        result["fallback_reason"] = str(e)

    print(json.dumps(result))


if __name__ == "__main__":
    main()
