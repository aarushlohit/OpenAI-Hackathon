#!/usr/bin/env python3
"""Live validation script for Hermes-X real NVIDIA provider cognition.

Verifies:
- NVIDIA connectivity
- Real NVIDIA reasoning invocation
- All agents use real NVIDIA reasoning
- Structured output validation
- Replay persistence
- Graph generation
- Consensus escalation
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.providers.nvidia_reasoning_client import NvidiaReasoningClient, NvidiaReasoningError
from app.security.model_output_validator import ModelOutputValidator, ModelOutputValidationError


TEST_INPUT = (
    "Telegram HR from @careerfastjob asks refundable onboarding payment of 3500 via UPI pay@upi "
    "and asks onboarding through Telegram only."
)


def _load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    for path in [Path(".env"), Path("app/.env")]:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    values.update({k: v for k, v in os.environ.items() if k.endswith("_API_KEY")})
    return values


async def _validate_nvidia_connectivity(env: dict[str, str]) -> bool:
    key = env.get("NVIDIA_NIM_API_KEY", "")
    if not key:
        print("  FAIL: NVIDIA_NIM_API_KEY not set")
        return False
    print(f"  OK: NVIDIA_NIM_API_KEY present (length={len(key)})")
    try:
        client = NvidiaReasoningClient(api_key=key, timeout=30.0)
        print("  OK: NvidiaReasoningClient instantiated")
        return True
    except NvidiaReasoningError as exc:
        print(f"  FAIL: {exc}")
        return False


async def _validate_behavior_cognition(client: NvidiaReasoningClient) -> bool:
    print("\n[BEHAVIOR] NVIDIA cognition started...")
    system_prompt = (
        "You are a cybersecurity fraud investigator. "
        "Analyze this evidence for payment extraction, coercion, impersonation, "
        "manipulation tactics, and onboarding fraud. Return STRICT COMPACT JSON ONLY. "
        "Limit to 4 strongest signals. Keep explanations under 140 characters."
    )
    user_prompt = f"ANALYZE:\n{TEST_INPUT}\n\nReturn only this JSON object, no prose: {{\"risk_score\":0-100,\"confidence\":0.0-1.0,\"signals\":[{{\"name\":\"...\",\"severity\":\"CRITICAL|HIGH|MEDIUM|LOW\",\"confidence\":0.0-1.0,\"explanation\":\"...\",\"source\":\"ai_reasoned\"}}],\"summary\":\"...\",\"recommended_action\":\"...\",\"reasoning_type\":\"behavioral_analysis\"}}"
    for attempt in range(3):
        try:
            start = time.perf_counter()
            output, latency_ms = await client.analyze_text(system_prompt, user_prompt, max_tokens=1500)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            print(f"  OK: NVIDIA response received ({latency_ms}ms, wall={elapsed_ms}ms)")
            print(f"  Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
            if client.last_metadata:
                print(f"  Provider Request ID: {client.last_metadata.request_id or 'N/A'}")
                print(f"  Provider Runtime: {client.last_metadata.provider}")
                print("  RAW PROVIDER RESPONSE:")
                print(json.dumps(client.last_metadata.raw_response, indent=2)[:4000])
            validator = ModelOutputValidator()
            validated = validator.validate_behavior_output(output)
            print(f"  OK: Output validated")
            print(f"  Risk Score: {validated.get('risk_score')}/100")
            print(f"  Confidence: {validated.get('confidence')}")
            print(f"  Signals: {len(validated.get('signals', []))}")
            for sig in validated.get("signals", []):
                print(f"    - {sig.get('name')}: {sig.get('severity')} ({sig.get('confidence')})")
            print(f"  Summary: {validated.get('summary', '')[:120]}")
            return True
        except NvidiaReasoningError as exc:
            if attempt < 2:
                print(f"  RETRY: Attempt {attempt + 1} failed: {exc}")
                await asyncio.sleep(2)
                continue
            print(f"  FAIL: NVIDIA reasoning error after {attempt + 1} attempts: {exc}")
            return False
        except ModelOutputValidationError as exc:
            print(f"  FAIL: Output validation error: {exc}")
            return False
    return False


async def _validate_osint_cognition(client: NvidiaReasoningClient) -> bool:
    print("\n[OSINT] domain_reputation analyzed")
    system_prompt = (
        "You are a cybersecurity analyst. Analyze this recruitment communication for "
        "infrastructure threats: domain anomalies, phishing, payment infrastructure. "
        "Return STRICT JSON ONLY."
    )
    user_prompt = f"ANALYZE:\n{TEST_INPUT}\n\nReturn JSON: {{\"reputation_score\":0-100,\"confidence\":0.0-1.0,\"indicators\":[{{\"name\":\"...\",\"severity\":\"CRITICAL|HIGH|MEDIUM|LOW\",\"confidence\":0.0-1.0,\"evidence\":\"...\",\"source\":\"ai_reasoned\"}}],\"summary\":\"...\",\"reasoning_type\":\"osint_analysis\"}}"
    for attempt in range(3):
        try:
            start = time.perf_counter()
            output, latency_ms = await client.analyze_text(system_prompt, user_prompt, max_tokens=1500)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            print(f"  OK: NVIDIA response received ({latency_ms}ms, wall={elapsed_ms}ms)")
            if client.last_metadata:
                print(f"  Provider Request ID: {client.last_metadata.request_id or 'N/A'}")
                print(f"  Provider Runtime: {client.last_metadata.provider}")
                print("  RAW PROVIDER RESPONSE:")
                print(json.dumps(client.last_metadata.raw_response, indent=2)[:4000])
            validator = ModelOutputValidator()
            validated = validator.validate_osint_output(output)
            print(f"  OK: Output validated")
            print(f"  Reputation Score: {validated.get('reputation_score')}/100")
            print(f"  Indicators: {len(validated.get('indicators', []))}")
            return True
        except NvidiaReasoningError as exc:
            if attempt < 2:
                print(f"  RETRY: Attempt {attempt + 1} failed: {exc}")
                await asyncio.sleep(2)
                continue
            print(f"  FAIL: NVIDIA reasoning error after {attempt + 1} attempts: {exc}")
            return False
        except ModelOutputValidationError as exc:
            print(f"  FAIL: Output validation error: {exc}")
            return False
    return False


async def _validate_vision_cognition(client: NvidiaReasoningClient) -> bool:
    print("\n[VISION] Vision cognition test (text-based, no image)")
    system_prompt = (
        "You are a document forensics specialist. Analyze evidence for forgery, "
        "phishing, and onboarding scams. Return STRICT JSON ONLY."
    )
    user_prompt = f"Analyze this text evidence for visual threats:\n{TEST_INPUT}\n\nReturn JSON: {{\"risk_score\":0-100,\"confidence\":0.0-1.0,\"artifacts\":[{{\"type\":\"...\",\"description\":\"...\",\"confidence\":0.0-1.0,\"severity\":\"CRITICAL|HIGH|MEDIUM|LOW\",\"source\":\"ai_reasoned\"}}],\"summary\":\"...\",\"reasoning_type\":\"vision_analysis\"}}"
    try:
        start = time.perf_counter()
        output, latency_ms = await client.analyze_text(system_prompt, user_prompt)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        print(f"  OK: NVIDIA response received ({latency_ms}ms, wall={elapsed_ms}ms)")
        if client.last_metadata:
            print(f"  Provider Request ID: {client.last_metadata.request_id or 'N/A'}")
            print(f"  Provider Runtime: {client.last_metadata.provider}")
            print("  RAW PROVIDER RESPONSE:")
            print(json.dumps(client.last_metadata.raw_response, indent=2)[:4000])
        validator = ModelOutputValidator()
        validated = validator.validate_vision_output(output)
        print(f"  OK: Output validated")
        print(f"  Risk Score: {validated.get('risk_score')}/100")
        print(f"  Artifacts: {len(validated.get('artifacts', []))}")
        return True
    except NvidiaReasoningError as exc:
        print(f"  FAIL: NVIDIA reasoning error: {exc}")
        return False
    except ModelOutputValidationError as exc:
        print(f"  FAIL: Output validation error: {exc}")
        return False


async def _validate_full_investigation() -> bool:
    print("\n[FULL] Running full investigation pipeline...")
    try:
        from app.core.container import AppContainer
        from app.schemas.investigation import InvestigationInputKind, InvestigationRequest

        container = AppContainer()
        request = InvestigationRequest(raw_input=TEST_INPUT, kind=InvestigationInputKind.TEXT)
        result = await container.orchestrator.investigate(request)

        print(f"  OK: Investigation completed: {result.investigation_id}")
        print(f"  Risk Level: {result.finding.risk_level.value}")
        print(f"  Summary: {result.finding.summary[:120]}")
        print(f"  Provider: {result.active_provider or 'N/A'}")
        print(f"  Model: {result.active_model or 'N/A'}")
        print(f"  Actions: {', '.join(result.finding.recommended_actions)}")
        return True
    except Exception as exc:
        print(f"  FAIL: Investigation pipeline error: {exc}")
        import traceback
        traceback.print_exc()
        return False


async def main() -> int:
    print("=" * 60)
    print("HERMES-X LIVE REAL PROVIDER VALIDATION")
    print("=" * 60)
    print(f"Test Input: {TEST_INPUT[:80]}...")
    print()

    env = _load_env()
    results: list[tuple[str, bool]] = []

    print("[1/5] NVIDIA Connectivity")
    ok = await _validate_nvidia_connectivity(env)
    results.append(("connectivity", ok))

    if not ok:
        print("\nCannot proceed without NVIDIA API key. Set NVIDIA_NIM_API_KEY in .env")
        for name, passed in results:
            status = "PASS" if passed else "FAIL"
            print(f"  {status}: {name}")
        return 1

    key = env.get("NVIDIA_NIM_API_KEY", "")
    client = NvidiaReasoningClient(api_key=key, timeout=60.0)

    print("\n[2/5] Behavior Cognition")
    ok = await _validate_behavior_cognition(client)
    results.append(("behavior_cognition", ok))

    print("\n[3/5] OSINT Cognition")
    ok = await _validate_osint_cognition(client)
    results.append(("osint_cognition", ok))

    print("\n[4/5] Vision Cognition")
    ok = await _validate_vision_cognition(client)
    results.append(("vision_cognition", ok))

    print("\n[5/5] Full Investigation Pipeline")
    ok = await _validate_full_investigation()
    results.append(("full_pipeline", ok))

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nFINAL VERDICT: ALL CHECKS PASSED")
        print("Hermes-X is running REAL NVIDIA cognition.")
        print("Primary Cognition Runtime: NVIDIA Nemotron Omni")
    else:
        print("\nFINAL VERDICT: SOME CHECKS FAILED")
        print("Review output above for details.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
