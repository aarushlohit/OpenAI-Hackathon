#!/usr/bin/env python3
"""Orchestrator: accept --text or --image and run corresponding agents.

This script forwards requests to `scripts/agents/text_agent.py` and
`scripts/agents/image_agent.py` so the TUI can launch "sub-agents".
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_agent(cmd: list) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(proc.stdout.strip())
    except Exception:
        return {"error": proc.stdout or proc.stderr}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--text", help="Path to text file", default=None)
    p.add_argument("--image", help="Path to image file", default=None)
    args = p.parse_args()

    if args.text:
        cmd = [sys.executable, str(Path(__file__).parent / "agents" / "text_agent.py"), "--file", args.text]
        res = run_agent(cmd)
        out = {"mode": "text", "result": res}
        print(json.dumps(out))
        return

    if args.image:
        cmd = [sys.executable, str(Path(__file__).parent / "agents" / "image_agent.py"), "--file", args.image]
        res = run_agent(cmd)
        out = {"mode": "image", "result": res}
        print(json.dumps(out))
        return

    print(json.dumps({"error": "no input provided"}))


if __name__ == "__main__":
    main()
