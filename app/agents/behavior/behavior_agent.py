from __future__ import annotations

import sys

from app.agents.base import AgentContext, InvestigationAgent
from app.models.behavior_result import BehaviorResult, BehaviorSignal
from app.providers.nvidia_reasoning_client import NVIDIA_MODEL, NvidiaReasoningClient
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationRequest
from app.security.model_output_validator import ModelOutputValidator


def _console_log(message: str) -> None:
    print(f"[BEHAVIOR] {message}", file=sys.stderr, flush=True)


_BEHAVIOR_SYSTEM_PROMPT = (
    "Return minified JSON only. Do not explain. Do not reason in prose. "
    "Analyze recruitment fraud risk. Use exactly one strongest signal."
)


class BehaviorAnalysisAgent(InvestigationAgent):
    name = "behavior"

    def __init__(self, prompt_registry: PromptRegistry, nvidia_client: NvidiaReasoningClient | None = None) -> None:
        self._prompt_registry = prompt_registry
        self._nvidia_client = nvidia_client
        self._validator = ModelOutputValidator()

    async def run(self, request: InvestigationRequest, context: AgentContext) -> BehaviorResult:
        await context.log(request, self.name, "Starting AI behavioral analysis")

        if self._nvidia_client is None:
            raise RuntimeError("NVIDIA runtime unavailable. Investigation aborted.")

        _console_log("NVIDIA cognition started...")
        _console_log(f"Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")

        user_prompt = (
            f"EVIDENCE:\n{request.raw_input}\n\n"
            "Return this JSON with real values: "
            '{"risk_score":0-100,"risk_level":"LOW|MEDIUM|HIGH|CRITICAL",'
            '"confidence":0.0-1.0,"signals":[{"name":"...",'
            '"severity":"LOW|MEDIUM|HIGH|CRITICAL","confidence":0.0-1.0,'
            '"source":"ai_reasoned","explanation":"max 40 chars"}],'
            '"summary":"max 80 chars","recommended_action":"max 60 chars",'
            '"reasoning_type":"behavioral_analysis"}'
        )

        ai_output, latency_ms = await self._nvidia_client.analyze_text(
            system_prompt=_BEHAVIOR_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.15,
            max_tokens=900,
        )
        _console_log(f"Response received ({latency_ms}ms)")

        validated = self._validator.validate_behavior_output(ai_output)

        ai_signals = [
            BehaviorSignal(
                name=sig.get("name", "unknown"),
                severity=sig.get("severity", "medium"),
                confidence=min(1.0, max(0.0, float(sig.get("confidence", 0.5)))),
                explanation=sig.get("explanation", "")[:1000],
                source=sig.get("source", "ai_reasoned"),
            )
            for sig in validated.get("signals", [])
        ]
        risk_score = min(100, max(0, int(validated.get("risk_score", 0))))
        confidence = min(1.0, max(0.0, float(validated.get("confidence", 0.5))))
        metadata = self._nvidia_client.last_metadata
        provider = metadata.provider if metadata else "nvidia_nim"
        model = metadata.model if metadata else NVIDIA_MODEL

        for sig in ai_signals:
            _console_log(f"  {sig.name}: {sig.severity.upper()} ({sig.confidence:.0%} confidence)")

        result = BehaviorResult(
            investigation_id=request.investigation_id,
            risk_score=risk_score,
            confidence=confidence,
            detected_patterns=[sig.name for sig in ai_signals],
            explanation=validated.get("summary", "")[:2000],
            provider=provider,
            provider_model=model,
            reasoning_type="behavioral_analysis",
            ai_signals=ai_signals,
            summary=validated.get("summary", "")[:500],
        )
        await context.log(
            request, self.name,
            f"Behavior analysis complete: risk_score={risk_score}, signals={len(ai_signals)}, provider={provider}"
        )
        return result
