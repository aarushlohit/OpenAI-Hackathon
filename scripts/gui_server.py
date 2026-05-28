#!/usr/bin/env python3
"""Minimal FastAPI GUI to submit text or image evidence to the orchestrator.

Endpoints:
- GET /          -> HTML form
- POST /api/text -> accepts `text` form field, forwards to `validate_input.py`
- POST /api/image -> accepts file upload `file`, saves temp file, forwards to `validate_input.py`

This server delegates to the existing `scripts/validate_input.py` so it uses the same
sub-agent flow (NIM for text, Pollinations for image when credentials are set).
"""
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import subprocess
import sys
import json
import shutil

APP_ROOT = Path(__file__).parent
VALIDATOR = APP_ROOT / "validate_input.py"

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    html = (APP_ROOT / "templates" / "index.html").read_text()
    return HTMLResponse(html)


def run_validator(args: list) -> dict:
    cmd = [sys.executable, str(VALIDATOR)] + args
    proc = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(proc.stdout)
    except Exception:
        return {"error": proc.stdout or proc.stderr}


@app.post("/api/text")
async def submit_text(text: str = Form(...)):
    # write temporary file
    tmp = APP_ROOT / "tmp_text_in.txt"
    tmp.write_text(text)
    res = run_validator(["--text", str(tmp)])
    return JSONResponse(res)


@app.post("/api/image")
async def submit_image(file: UploadFile = File(...)):
    tmp_dir = APP_ROOT / "tmp_uploads"
    tmp_dir.mkdir(exist_ok=True)
    dest = tmp_dir / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    res = run_validator(["--image", str(dest)])
    return JSONResponse(res)


if __name__ == "__main__":
    print("Run with: uvicorn scripts.gui_server:app --reload --port 9000")
