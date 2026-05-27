from time import perf_counter

from app.agents.base import AgentContext, InvestigationAgent
from app.contracts.agent_result import AgentResult
from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName
from app.models.behavior_result import BehaviorResult
from app.models.osint_result import OSINTResult
from app.models.threat_score import ThreatScore, ThreatSeverity
from app.models.vision_result import VisionResult
from app.memory.models import MemoryRecord
from app.memory.repository import MemoryRepository
from app.observability import AgentMetrics, AgentTrace
from app.schemas.investigation import (
    EvidenceItem,
    InvestigationFinding,
    InvestigationRequest,
    InvestigationResult,
    RiskLevel,
)
from app.scoring import ThreatScoringEngine


class InvestigationOrchestrator:
    def __init__(
        self,
        agents: list[InvestigationAgent],
        event_bus: InMemoryEventBus,
        memory_repository: MemoryRepository,
        scoring_engine: ThreatScoringEngine,
        agent_metrics: AgentMetrics,
    ) -> None:
        self._agents = agents
        self._event_bus = event_bus
        self._memory_repository = memory_repository
        self._scoring_engine = scoring_engine
        self._agent_metrics = agent_metrics

    async def investigate(self, request: InvestigationRequest) -> InvestigationResult:
        await self._event_bus.publish(
            EventEnvelope(
                event=EventName.INVESTIGATION_REQUESTED,
                correlation_id=request.correlation_id,
                payload={
                    "investigation_id": request.investigation_id,
                    "kind": request.kind.value,
                    "input_length": len(request.raw_input),
                },
            )
        )
        context = AgentContext(self._event_bus)
        agent_results: list[AgentResult] = []
        for agent in self._agents:
            await self._event_bus.publish(
                EventEnvelope(
                    event=EventName.AGENT_STARTED,
                    correlation_id=request.correlation_id,
                    agent=agent.name,
                    payload={"investigation_id": request.investigation_id},
                )
            )
            started = perf_counter()
            result = await agent.run(request, context)
            duration_ms = int((perf_counter() - started) * 1000)
            self._agent_metrics.record(
                AgentTrace(
                    investigation_id=request.investigation_id,
                    agent=agent.name,
                    latency_ms=duration_ms,
                    success=True,
                )
            )
            if result is not None:
                agent_results.append(result)
            await self._event_bus.publish(
                EventEnvelope(
                    event=EventName.AGENT_COMPLETED,
                    correlation_id=request.correlation_id,
                    agent=agent.name,
                    payload={
                        "investigation_id": request.investigation_id,
                        "duration_ms": duration_ms,
                    },
                )
            )

        threat_score = await self._scoring_engine.score(request.investigation_id, agent_results)
        if threat_score.severity in {ThreatSeverity.HIGH, ThreatSeverity.CRITICAL}:
            await self._event_bus.publish(
                EventEnvelope(
                    event=EventName.THREAT_DETECTED,
                    correlation_id=request.correlation_id,
                    payload=threat_score.model_dump(mode="json"),
                )
            )

        result = InvestigationResult(
            investigation_id=request.investigation_id,
            correlation_id=request.correlation_id,
            finding=InvestigationFinding(
                summary=threat_score.explanation,
                risk_level=self._risk_level(threat_score),
                evidence=self._evidence_from_results(agent_results),
                recommended_actions=[
                    "Review evidence before taking enforcement action.",
                    "Keep original artifacts isolated until sandbox scanning is implemented.",
                ],
            ),
        )
        await self._memory_repository.append(
            MemoryRecord(
                correlation_id=request.correlation_id,
                namespace="investigation",
                key="phase_3_result",
                value={
                    "result": result.model_dump(mode="json"),
                    "agent_results": [agent_result.model_dump(mode="json") for agent_result in agent_results],
                    "threat_score": threat_score.model_dump(mode="json"),
                },
            )
        )
        await self._event_bus.publish(
            EventEnvelope(
                event=EventName.INVESTIGATION_COMPLETED,
                correlation_id=request.correlation_id,
                payload={
                    "investigation_id": request.investigation_id,
                    "risk_level": result.finding.risk_level.value,
                    "score": threat_score.final_score,
                },
            )
        )
        return result

    def _risk_level(self, threat_score: ThreatScore) -> RiskLevel:
        mapping = {
            ThreatSeverity.LOW: RiskLevel.LOW,
            ThreatSeverity.MEDIUM: RiskLevel.MEDIUM,
            ThreatSeverity.HIGH: RiskLevel.HIGH,
            ThreatSeverity.CRITICAL: RiskLevel.CRITICAL,
        }
        return mapping[threat_score.severity]

    def _evidence_from_results(self, results: list[AgentResult]) -> list[EvidenceItem]:
        evidence: list[EvidenceItem] = []
        for result in results:
            if isinstance(result, BehaviorResult):
                evidence.append(
                    EvidenceItem(
                        label="Behavior analysis",
                        detail=result.explanation,
                        confidence=result.confidence,
                    )
                )
            elif isinstance(result, OSINTResult):
                detail = ", ".join(result.suspicious_indicators) or "No suspicious OSINT indicator found."
                evidence.append(
                    EvidenceItem(label="OSINT analysis", detail=detail, confidence=result.confidence)
                )
            elif isinstance(result, VisionResult):
                detail = ", ".join(result.suspicious_elements) or "No suspicious visual element found."
                evidence.append(
                    EvidenceItem(label="Vision analysis", detail=detail, confidence=result.confidence)
                )
        return evidence
