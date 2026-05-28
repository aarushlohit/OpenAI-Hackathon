"""
Hermes-X Backend — Clean MVP
FastAPI server with SSE streaming investigation endpoint.
"""

import json
import asyncio
import sys
import os
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env from this directory
load_dotenv(Path(__file__).parent / ".env")

# Ensure agents/providers/utils are importable
sys.path.insert(0, str(Path(__file__).parent))

import agents.behavior_agent as behavior_agent
import agents.osint_agent as osint_agent
import agents.domain_agent as domain_agent
import agents.consensus_agent as consensus_agent
from providers import pollinations_client

app = FastAPI(title="Hermes-X", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main SPA."""
    html_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "hermes-x", "version": "2.0.0"}


def _sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _run_investigation(text: str, image_bytes: bytes | None, mime_type: str) -> AsyncGenerator[str, None]:
    """
    Core investigation pipeline — yields SSE events.
    All agents run in a thread pool to avoid blocking the event loop.
    """
    loop = asyncio.get_event_loop()

    # Step 1: Behavior
    yield _sse("progress", {"step": "behavior", "message": "Analyzing onboarding flow and communication patterns…"})
    behavior_result = await loop.run_in_executor(None, behavior_agent.run, text)
    yield _sse("agent_result", {"agent": "behavior", "result": behavior_result})

    # Step 2: OSINT
    yield _sse("progress", {"step": "osint", "message": "Verifying company legitimacy and recruiter claims…"})
    osint_result = await loop.run_in_executor(None, osint_agent.run, text)
    yield _sse("agent_result", {"agent": "osint", "result": osint_result})

    # Step 3: Domain
    yield _sse("progress", {"step": "domain", "message": "Checking domain trust and typo-squatting indicators…"})
    domain_result = await loop.run_in_executor(None, domain_agent.run, text)
    yield _sse("agent_result", {"agent": "domain", "result": domain_result})

    # Step 4: Image (optional)
    image_analysis = None
    if image_bytes:
        yield _sse("progress", {"step": "image", "message": "Analyzing attached image for fraud indicators…"})
        try:
            image_analysis = await loop.run_in_executor(
                None,
                lambda: pollinations_client.analyze_image(
                    image_bytes,
                    "Analyze this image for signs of recruitment fraud, suspicious company logos, "
                    "fake offer letters, suspicious payment instructions, or other scam indicators. "
                    "Be specific about what you see.",
                    mime_type,
                ),
            )
            yield _sse("agent_result", {"agent": "image", "result": {"analysis": image_analysis}})
        except RuntimeError as e:
            yield _sse("agent_result", {"agent": "image", "result": {"error": str(e)}})

    # Step 5: Consensus
    yield _sse("progress", {"step": "consensus", "message": "Running consensus analysis and forming final verdict…"})
    consensus_result = await loop.run_in_executor(
        None,
        lambda: consensus_agent.run(behavior_result, osint_result, domain_result, image_analysis),
    )

    yield _sse("verdict", {
        "consensus": consensus_result,
        "technical": {
            "behavior": behavior_result,
            "osint": osint_result,
            "domain": domain_result,
            "image": {"analysis": image_analysis} if image_analysis else None,
        },
    })

    yield _sse("done", {"message": "Investigation complete"})


@app.post("/investigate")
async def investigate(
    text: str = Form(""),
    image: UploadFile | None = File(None),
):
    """
    Main investigation endpoint. Returns SSE stream.
    Accepts text and optional image upload.
    """
    if not text.strip() and image is None:
        return StreamingResponse(
            iter([_sse("error", {"message": "Please provide text or an image to investigate."})]),
            media_type="text/event-stream",
        )

    image_bytes = None
    mime_type = "image/jpeg"
    if image is not None:
        image_bytes = await image.read()
        mime_type = image.content_type or "image/jpeg"

    return StreamingResponse(
        _run_investigation(text, image_bytes, mime_type),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
