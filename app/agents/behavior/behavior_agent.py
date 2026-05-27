from dataclasses import dataclass

from app.agents.base import AgentContext, InvestigationAgent
from app.models.behavior_result import BehaviorResult
from app.prompts import PromptRegistry
from app.schemas.investigation import InvestigationRequest
from app.services.scoring import clamp_score


@dataclass(frozen=True)
class BehaviorPattern:
    label: str
    terms: tuple[str, ...]
    weight: int


class BehaviorAnalysisAgent(InvestigationAgent):
    name = "behavior"

    patterns = (
        BehaviorPattern("urgency_manipulation", ("urgent", "immediately", "limited time", "today"), 16),
        BehaviorPattern("payment_coercion", ("deposit", "fee", "payment", "pay now"), 30),
        BehaviorPattern("fake_prestige", ("top mnc", "fortune", "guaranteed job", "exclusive"), 12),
        BehaviorPattern("emotional_pressure", ("trust me", "do not miss", "last chance"), 12),
        BehaviorPattern("scarcity_tactics", ("only few seats", "limited slots", "first come"), 14),
        BehaviorPattern("authority_abuse", ("hr head", "director approval", "official mandate"), 12),
        BehaviorPattern("telegram_only_onboarding", ("telegram", "join channel", "telegram group"), 20),
        BehaviorPattern("interview_bypass", ("no interview", "direct offer", "selected without interview"), 24),
        BehaviorPattern("refundable_deposit", ("refundable deposit", "security deposit"), 32),
    )

    def __init__(self, prompt_registry: PromptRegistry) -> None:
        self._prompt_registry = prompt_registry

    async def run(self, request: InvestigationRequest, context: AgentContext) -> BehaviorResult:
        await context.log(request, self.name, "Scanning recruitment language for social engineering patterns")
        self._prompt_registry.load("behavior", "system_prompt")
        lowered = request.raw_input.lower()
        detected = [pattern for pattern in self.patterns if any(term in lowered for term in pattern.terms)]
        labels = [pattern.label for pattern in detected]
        score = clamp_score(sum(pattern.weight for pattern in detected))
        confidence = min(0.95, 0.35 + (len(detected) * 0.12))
        explanation = self._explain(labels)
        await context.log(request, self.name, f"Detected {len(labels)} behavior pattern(s)")
        return BehaviorResult(
            investigation_id=request.investigation_id,
            risk_score=score,
            confidence=confidence,
            detected_patterns=labels,
            explanation=explanation,
        )

    def _explain(self, labels: list[str]) -> str:
        if not labels:
            return "No high-risk social engineering pattern was detected in the supplied text."
        readable = ", ".join(label.replace("_", " ") for label in labels)
        return f"Detected high-risk social engineering patterns: {readable}. Findings are evidence-based and not a definitive accusation."

