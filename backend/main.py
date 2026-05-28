"""
Hermes-X Backend — Clean MVP
FastAPI server with SSE streaming investigation endpoint.
"""

import json
import asyncio
import sys
import os
import re
import time
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import Depends, FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load env from repo root and backend directory. Secrets stay outside source.
load_dotenv(Path(__file__).parents[1] / ".env")
load_dotenv(Path(__file__).parent / ".env")

# Ensure agents/providers/utils are importable
sys.path.insert(0, str(Path(__file__).parent))

import agents.behavior_agent as behavior_agent
import agents.osint_agent as osint_agent
import agents.domain_agent as domain_agent
import agents.reputation_agent as reputation_agent
import agents.consensus_agent as consensus_agent
from auth.middleware import optional_user
from auth.routes import router as auth_router
from database.mongodb import ensure_indexes
from providers import mongo_client, opencode_client, pollinations_client
from security_headers import SecurityMiddleware, allowed_origins

app = FastAPI(title="Detective Hermes Agent", version="2.0.0")
app.include_router(auth_router)
app.add_middleware(SecurityMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins()),
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)

STATIC_DIR = Path(__file__).parent / "static"
REACT_DIST_DIR = Path(__file__).parents[1] / "frontend" / "react_app" / "dist"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
if (REACT_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(REACT_DIST_DIR / "assets")), name="react-assets")


@app.on_event("startup")
async def startup():
    await ensure_indexes()


@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
@app.get("/signup", response_class=HTMLResponse)
@app.get("/app", response_class=HTMLResponse)
async def index():
    """Serve the main SPA."""
    html_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(), status_code=200)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "detective-hermes-agent",
        "version": "2.0.0",
        "mongodb": mongo_client.enabled(),
        "opencode_api": bool(os.getenv("OPENCODE_API_KEY") or os.getenv("OPENROUTER_API_KEY")),
    }


@app.get("/api/history")
async def history(user: dict[str, Any] | None = Depends(optional_user)):
    if not user:
        return {"items": []}
    return {"items": mongo_client.list_investigations(user_id=user["id"])}


@app.get("/api/reports")
async def reports(user: dict[str, Any] | None = Depends(optional_user)):
    if not user:
        return {"items": []}
    return {"items": mongo_client.list_reports(user_id=user["id"])}


@app.post("/api/reports")
async def save_report(record: dict[str, Any], user: dict[str, Any] | None = Depends(optional_user)):
    if user:
        record["user_id"] = user["id"]
    return mongo_client.save_report(record)


def _sse(event: str, data: dict) -> str:
    """Format a Server-Sent Event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _run_investigation(
    text: str,
    image_bytes: bytes | None,
    mime_type: str,
    image_filename: str = "evidence.jpg",
    image_path: str = "",
    user_id: str | None = None,
) -> AsyncGenerator[str, None]:
    """
    Core investigation pipeline — yields SSE events.
    All agents run in a thread pool to avoid blocking the event loop.
    """
    loop = asyncio.get_event_loop()
    image_analysis = None
    investigation_id = f"case-{int(time.time() * 1000)}"

    yield _sse("progress", {"step": "thinking", "message": "Thinking…"})
    yield _sse("progress", {"step": "pondering", "message": "Pondering evidence boundaries…"})
    yield _sse("progress", {"step": "agents", "message": "Launching agents…"})

    # Step 1: Image OCR / extraction (optional). This runs first so image-only
    # evidence can still feed text, domain, and company analysis.
    if image_bytes:
        if user_id:
            await loop.run_in_executor(
                None,
                lambda: mongo_client.save_uploaded_metadata({
                    "user_id": user_id,
                    "case_id": investigation_id,
                    "filename": image_filename,
                    "mime_type": mime_type,
                    "size_bytes": len(image_bytes),
                    "image_path": image_path,
                }),
            )
        yield _sse("progress", {"step": "image", "message": "Launching Agent<ImageForensics>…"})
        yield _sse("progress", {"step": "image", "message": "Uploading image and extracting offer-letter text…"})
        try:
            image_analysis = await loop.run_in_executor(
                None,
                lambda: pollinations_client.extract_offer_letter(
                    image_bytes,
                    image_filename,
                    mime_type,
                ),
            )
            yield _sse("agent_result", {"agent": "image", "result": image_analysis})
        except RuntimeError as e:
            image_analysis = {"error": str(e), "provider": pollinations_client.model_name()}
            yield _sse("agent_result", {"agent": "image", "result": image_analysis})

    analysis_text = _merge_text_and_image_extraction(text, image_analysis)

    # Step 2: Behavior
    yield _sse("progress", {"step": "behavior", "message": "Launching Agent<Behavior>…"})
    yield _sse("progress", {"step": "behavior", "message": "Analyzing onboarding flow and communication patterns…"})
    behavior_result = await loop.run_in_executor(None, behavior_agent.run, analysis_text)
    yield _sse("agent_result", {"agent": "behavior", "result": behavior_result})

    # Step 3: OSINT
    yield _sse("progress", {"step": "osint", "message": "Launching Agent<OSINT>…"})
    yield _sse("progress", {"step": "osint", "message": "Verifying company legitimacy and recruiter claims…"})
    osint_result = await loop.run_in_executor(None, osint_agent.run, analysis_text)
    yield _sse("agent_result", {"agent": "osint", "result": osint_result})

    # Step 4: Domain
    yield _sse("progress", {"step": "domain", "message": "Launching Agent<DomainIntel>…"})
    yield _sse("progress", {"step": "domain", "message": "Checking domain trust and typo-squatting indicators…"})
    domain_result = await loop.run_in_executor(None, domain_agent.run, analysis_text)
    yield _sse("agent_result", {"agent": "domain", "result": domain_result})

    # Step 5: Web reputation. A registered company can still be tied to fake
    # internships, deposit fraud, or impersonation, so search public reputation
    # sources before final synthesis.
    yield _sse("progress", {"step": "web", "message": "Launching Agent<WebReputation>…"})
    yield _sse("progress", {"step": "web", "message": "Searching Glassdoor, AmbitionBox, Reddit, and scam reports…"})
    web_reputation_result = await loop.run_in_executor(
        None,
        lambda: opencode_client.search_company_reputation(
            {
                "operator_text": text,
                "analysis_text": analysis_text,
                "image_extraction": image_analysis,
                "behavior": behavior_result,
                "osint": osint_result,
                "domain": domain_result,
            }
        ),
    )
    yield _sse("agent_result", {"agent": "web", "result": web_reputation_result})

    # Step 5b: Reputation Intelligence — evaluates educational value, exploitation signals,
    # certificate farming, and public trust quality (separate from fraud detection)
    yield _sse("progress", {"step": "reputation", "message": "Launching Agent<ReputationIntel>…"})
    yield _sse("progress", {"step": "reputation", "message": "Evaluating educational value, trust quality, and exploitation signals…"})
    reputation_result = await loop.run_in_executor(
        None,
        lambda: reputation_agent.run(
            analysis_text,
            osint_result=osint_result,
            web_reputation=web_reputation_result,
        ),
    )
    yield _sse("agent_result", {"agent": "reputation", "result": reputation_result})

    # Step 6: Consensus
    yield _sse("progress", {"step": "consensus", "message": "Launching Agent<TrustSynthesis>…"})
    yield _sse("progress", {"step": "consensus", "message": "Synthesizing trust intelligence and forming final verdict…"})
    consensus_result = await loop.run_in_executor(
        None,
        lambda: consensus_agent.run(
            behavior_result,
            osint_result,
            domain_result,
            reputation=reputation_result,
            image_analysis=image_analysis,
            web_reputation=web_reputation_result,
        ),
    )

    # Step 7: OpenCode final review
    yield _sse("progress", {"step": "opencode", "message": "Launching Agent<OpenCodeDeepSeek>…"})
    yield _sse("progress", {"step": "opencode", "message": "Parsing evidence through OpenCode DeepSeek review…"})
    opencode_result = await loop.run_in_executor(
        None,
        lambda: opencode_client.assess_offer_letter(
            {
                "operator_text": text,
                "analysis_text": analysis_text,
                "image_extraction": image_analysis,
                "behavior": behavior_result,
                "osint": osint_result,
                "domain": domain_result,
                "web_reputation": web_reputation_result,
                "consensus": consensus_result,
            }
        ),
    )
    yield _sse("agent_result", {"agent": "opencode", "result": opencode_result})

    final_consensus = _merge_opencode_verdict(consensus_result, opencode_result, web_reputation_result, reputation_result)
    technical = {
        "behavior": behavior_result,
        "osint": osint_result,
        "domain": domain_result,
        "image": image_analysis,
        "web": web_reputation_result,
        "reputation": reputation_result,
        "opencode": opencode_result,
    }
    record = _build_investigation_record(
        investigation_id,
        text,
        final_consensus,
        technical,
        user_id=user_id,
        image_path=image_path,
        image_filename=image_filename if image_bytes else "",
    )
    storage = await loop.run_in_executor(None, lambda: mongo_client.save_investigation(record))

    yield _sse("verdict", {
        "id": investigation_id,
        "storage": storage,
        "consensus": final_consensus,
        "technical": {
            "behavior": behavior_result,
            "osint": osint_result,
            "domain": domain_result,
            "image": image_analysis,
            "web": web_reputation_result,
            "reputation": reputation_result,
            "opencode": opencode_result,
        },
    })

    yield _sse("done", {"message": "Investigation complete"})


@app.post("/investigate")
async def investigate(
    text: str = Form(""),
    image: UploadFile | None = File(None),
    image_path: str = Form(""),
    user: dict[str, Any] | None = Depends(optional_user),
):
    """
    Main investigation endpoint. Returns SSE stream.
    Accepts text and optional image upload.
    """
    if not text.strip() and image is None and not image_path.strip():
        return StreamingResponse(
            iter([_sse("error", {"message": "Please provide text or an image to investigate."})]),
            media_type="text/event-stream",
        )

    image_bytes = None
    mime_type = "image/jpeg"
    image_filename = "evidence.jpg"
    if image is not None:
        image_bytes = await image.read()
        mime_type = image.content_type or "image/jpeg"
        image_filename = image.filename or image_filename
    elif image_path.strip():
        try:
            image_bytes, image_filename, mime_type = pollinations_client.load_image_from_path(image_path.strip())
        except RuntimeError as e:
            return StreamingResponse(
                iter([_sse("error", {"message": str(e)})]),
                media_type="text/event-stream",
            )

    return StreamingResponse(
        _run_investigation(
            text,
            image_bytes,
            mime_type,
            image_filename,
            image_path=image_path.strip(),
            user_id=user["id"] if user else None,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _merge_text_and_image_extraction(text: str, image_analysis: dict | None) -> str:
    parts = []
    if text.strip():
        parts.append(text.strip())
    if image_analysis:
        extracted_text = image_analysis.get("extracted_text")
        offer_summary = image_analysis.get("offer_summary")
        company_name = image_analysis.get("company_name")
        scam_conclusion = image_analysis.get("scam_conclusion")
        red_flags = image_analysis.get("red_flags") or []
        safe_signals = image_analysis.get("safe_signals") or []

        image_parts = []
        if company_name:
            image_parts.append(f"Company from image: {company_name}")
        if extracted_text:
            image_parts.append(f"Extracted offer-letter text:\n{extracted_text}")
        if offer_summary:
            image_parts.append(f"Offer summary: {offer_summary}")
        if scam_conclusion:
            image_parts.append(f"Pollinations image conclusion: {scam_conclusion}")
        if red_flags:
            image_parts.append(f"Image red flags: {json.dumps(red_flags, ensure_ascii=False)}")
        if safe_signals:
            image_parts.append(f"Image safe signals: {json.dumps(safe_signals, ensure_ascii=False)}")
        if image_parts:
            parts.append("\n".join(image_parts))

    return "\n\n".join(parts) or "(image-only evidence; extraction unavailable)"


def _merge_opencode_verdict(
    consensus: dict,
    opencode: dict,
    web_reputation: dict | None = None,
    reputation: dict | None = None,
) -> dict:
    """Merge OpenCode trust tier with consensus, applying nuanced trust-tier logic."""
    merged = dict(consensus)

    # Trust tier ordering — higher index = worse trust
    _TIERS = ["LEGITIMATE", "LOW TRUST OPPORTUNITY", "SUSPICIOUS", "HIGH RISK", "CRITICAL"]

    def _tier_rank(v: str) -> int:
        v = v.upper().strip()
        for i, t in enumerate(_TIERS):
            if v == t or v == t.replace(" ", "_"):
                return i
        # Legacy binary vocab mapping
        if "CRITICAL" in v: return 4
        if "HIGH" in v: return 3
        if "SUSPICIOUS" in v or "MEDIUM" in v or "UNCERTAIN" in v: return 2
        if "LOW" in v or "LOW_TRUST" in v: return 1
        if "SAFE" in v or "NOT SCAM" in v or "LEGITIMATE" in v: return 0
        return 2  # default: suspicious

    def _rank_to_verdict(rank: int) -> str:
        return _TIERS[max(0, min(rank, len(_TIERS) - 1))]

    current_rank = _tier_rank(merged.get("verdict", "SUSPICIOUS"))

    # --- Web reputation input ---
    if web_reputation:
        web_conclusion = str(web_reputation.get("conclusion", "")).upper()
        registered_but_suspicious = web_reputation.get("registered_but_suspicious", False)
        cert_farming = web_reputation.get("certificate_farming_signals", False)
        web_scam_signals = [str(s) for s in (web_reputation.get("scam_signals") or [])]
        exploitation_signals = [str(s) for s in (web_reputation.get("exploitation_signals") or [])]
        web_summary = web_reputation.get("summary", "")

        web_rank = _tier_rank(web_conclusion)
        # Blend: push verdict toward web rank but cap escalation at +1 tier
        if web_rank > current_rank:
            current_rank = min(current_rank + 1, web_rank)

        if cert_farming and current_rank < 2:
            current_rank = max(current_rank, 1)  # at least LOW_TRUST

        if registered_but_suspicious and current_rank < 1:
            current_rank = 1  # at least LOW_TRUST

        if web_scam_signals:
            existing = merged.get("why_flagged") or []
            merged["why_flagged"] = list(dict.fromkeys([*existing, *web_scam_signals]))[:8]
        if exploitation_signals:
            existing = merged.get("exploitation_signals") or []
            merged["exploitation_signals"] = list(dict.fromkeys([*existing, *exploitation_signals]))[:6]
        if web_summary:
            merged["reasoning"] = f"{merged.get('reasoning', '')} Web: {web_summary}".strip()

    # --- Reputation agent input ---
    if reputation:
        rep_trust_tier = reputation.get("trust_tier", "")
        rep_rank = _tier_rank(rep_trust_tier) if rep_trust_tier else 2
        exploitation = [str(s) for s in (reputation.get("exploitation_signals") or [])]

        # Reputation can lower verdict (toward safer) but not escalate past HIGH RISK
        if rep_rank != current_rank:
            # Average toward reputation rank, capped conservatively
            blended = (current_rank + rep_rank) // 2
            # Reputation alone can't push past HIGH RISK (rank 3) — requires fraud evidence
            current_rank = min(blended, 3) if current_rank < 3 else current_rank

        if exploitation:
            existing = merged.get("exploitation_signals") or []
            merged["exploitation_signals"] = list(dict.fromkeys([*existing, *exploitation]))[:6]

    # --- OpenCode final review ---
    if opencode and not opencode.get("error"):
        oc_conclusion = str(opencode.get("conclusion", "")).upper()
        if oc_conclusion:
            oc_rank = _tier_rank(oc_conclusion)
            # OpenCode is authoritative — allow it to push up OR down by up to 1 tier
            if oc_rank > current_rank:
                current_rank = min(current_rank + 1, oc_rank)
            elif oc_rank < current_rank:
                current_rank = max(current_rank - 1, oc_rank)

        confidence = opencode.get("confidence")
        if isinstance(confidence, (int, float)):
            normalized = confidence * 100 if 0 <= confidence <= 1 else confidence
            merged["confidence"] = max(0, min(100, int(normalized)))

        summary = opencode.get("summary")
        if summary:
            merged["headline"] = _first_sentence(str(summary)) or merged.get("headline", "")
            merged["reasoning"] = f"{merged.get('reasoning', '')} OpenCode: {summary}".strip()

        evidence = opencode.get("key_evidence")
        if isinstance(evidence, list) and evidence:
            existing = merged.get("why_flagged") or []
            merged["why_flagged"] = list(dict.fromkeys([*existing, *[str(e) for e in evidence]]))[:8]

        oc_exploitation = opencode.get("exploitation_signals") or []
        if oc_exploitation:
            existing = merged.get("exploitation_signals") or []
            merged["exploitation_signals"] = list(dict.fromkeys([*existing, *[str(e) for e in oc_exploitation]]))[:6]

        action = opencode.get("recommended_action")
        if action:
            merged["recommendation"] = str(action)

        merged["opencode_provider"] = opencode.get("provider")

    merged["verdict"] = _rank_to_verdict(current_rank)
    return merged



def _first_sentence(text: str) -> str:
    match = re.match(r"(.+?[.!?])(?:\s|$)", text.strip())
    return match.group(1) if match else text.strip()[:160]


def _build_investigation_record(
    investigation_id: str,
    text: str,
    consensus: dict[str, Any],
    technical: dict[str, Any],
    user_id: str | None = None,
    image_path: str = "",
    image_filename: str = "",
) -> dict[str, Any]:
    company = (
        (technical.get("image") or {}).get("company_name")
        or (technical.get("web") or {}).get("company")
        or (technical.get("opencode") or {}).get("company")
        or "Unknown company"
    )
    return {
        "id": investigation_id,
        "user_id": user_id,
        "created_at": datetime_like_iso(),
        "title": consensus.get("headline") or consensus.get("verdict") or "Investigation",
        "company": company,
        "verdict": consensus.get("verdict", "UNKNOWN"),
        "confidence": consensus.get("confidence", 0),
        "recommendation": consensus.get("recommendation", ""),
        "summary": consensus.get("reasoning", ""),
        "input_preview": text[:500],
        "input_text": text[:5000],
        "image_path": image_path,
        "image_filename": image_filename,
        "provider": (
            (technical.get("opencode") or {}).get("provider")
            or (technical.get("web") or {}).get("provider")
            or "hermes-agents"
        ),
        "technical": technical,
    }


def datetime_like_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
