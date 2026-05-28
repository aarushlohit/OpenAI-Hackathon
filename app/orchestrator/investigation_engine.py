import asyncio
from time import perf_counter

from app.agents.base import AgentContext, InvestigationAgent
from app.contracts.agent_result import AgentResult
from app.events.bus import InMemoryEventBus
from app.events.models import EventEnvelope, EventName
from app.graph import ThreatGraphEngine
from app.intelligence import ThreatCorrelationEngine
from app.intelligence import ReputationCorrelationEngine
from app.memory.context_snapshots import ContextSnapshotStore
from app.memory.investigation_repository import InvestigationRepository
from app.memory.session_memory import SessionMemory
from app.memory.threat_memory import ThreatMemory
from app.models.behavior_result import BehaviorResult
from app.models.audio_result import AudioResult
from app.models.osint_result import OSINTResult
from app.models.threat_score import ThreatScore, ThreatSeverity
from app.models.vision_result import VisionResult
from app.models.web_search_result import WebSearchResult
from app.observability import AgentMetrics, AgentTrace, GraphMetrics, ProviderMetrics, ProviderTrace
from app.orchestrator.context_manager import InvestigationContextManager
from app.orchestrator.pipeline_router import PipelineRouter
from app.reporting import ReportBuilder
from app.schemas.investigation import (
    EvidenceItem,
    InvestigationFinding,
    InvestigationRequest,
    InvestigationResult,
    RiskLevel,
)
from app.scoring import ThreatScoringEngine


class InvestigationEngine:
    def __init__(
        self,
        agents: list[InvestigationAgent],
        event_bus: InMemoryEventBus,
        pipeline_router: PipelineRouter,
        context_manager: InvestigationContextManager,
        investigation_repository: InvestigationRepository,
        session_memory: SessionMemory,
        snapshot_store: ContextSnapshotStore,
        scoring_engine: ThreatScoringEngine,
        correlation_engine: ReputationCorrelationEngine,
        threat_graph_engine: ThreatGraphEngine,
        threat_correlation_engine: ThreatCorrelationEngine,
        threat_memory: ThreatMemory,
        report_builder: ReportBuilder,
        agent_metrics: AgentMetrics,
        graph_metrics: GraphMetrics,
        provider_metrics: ProviderMetrics,
        agent_timeout_seconds: float = 15.0,
    ) -> None:
        self._agents = {agent.name: agent for agent in agents}
        self._event_bus = event_bus
        self._pipeline_router = pipeline_router
        self._context_manager = context_manager
        self._investigation_repository = investigation_repository
        self._session_memory = session_memory
        self._snapshot_store = snapshot_store
        self._scoring_engine = scoring_engine
        self._correlation_engine = correlation_engine
        self._threat_graph_engine = threat_graph_engine
        self._threat_correlation_engine = threat_correlation_engine
        self._threat_memory = threat_memory
        self._report_builder = report_builder
        self._agent_metrics = agent_metrics
        self._graph_metrics = graph_metrics
        self._provider_metrics = provider_metrics
        self._agent_timeout_seconds = agent_timeout_seconds

    async def investigate(self, request: InvestigationRequest) -> InvestigationResult:
        workflow_started = perf_counter()
        workflow = self._pipeline_router.route(request)
        context = self._context_manager.create(request)
        await self._session_memory.put(context)
        await self._snapshot_store.append(context)
        await self._investigation_repository.save_context(context)
        await self._publish(request, EventName.INVESTIGATION_STARTED, {"workflow": workflow.name})
        await self._publish(request, EventName.INVESTIGATION_PROGRESS, {"message": "Classifying evidence"})
        for message in (
            "Analyzing recruiter behavior...",
            "Evaluating onboarding legitimacy...",
            "Checking domain intelligence...",
            "Verifying company legitimacy on the web...",
            "Correlating threat graph...",
            "Validating payment coercion signals...",
            "Running cross-agent consensus...",
            "Generating explainable verdict...",
        ):
            await self._publish(request, EventName.INVESTIGATION_PROGRESS, {"message": message})
        
        # Track active provider from metrics
        active_provider = None
        active_model = None

        results: list[AgentResult] = []
        for agent_name in workflow.required_agents:
            try:
                result = await self._run_agent(agent_name, request)
            except Exception as error:
                raise RuntimeError("NVIDIA runtime unavailable. Investigation aborted.") from error
            if result is not None:
                results.append(result)
                context = context.with_result(result)

        parallel_results = await asyncio.gather(
            *(self._run_agent(agent_name, request) for agent_name in workflow.parallel_agents),
            return_exceptions=True,
        )
        for result in parallel_results:
            if isinstance(result, Exception):
                import traceback
                print("--- INNER EXCEPTION ---")
                traceback.print_exception(type(result), result, result.__traceback__)
                print("-----------------------")
                await self._publish(request, EventName.INVESTIGATION_PROGRESS, {"warning": str(result)})
                raise RuntimeError("NVIDIA runtime unavailable. Investigation aborted.") from result
            if result is not None:
                results.append(result)
                context = context.with_result(result)

        correlation = await self._correlation_engine.correlate(context)
        context.metadata["correlation_indicators"] = ",".join(correlation.indicators)
        await self._snapshot_store.append(context)
        await self._investigation_repository.save_context(context)
        graph_projection = await self._threat_graph_engine.project(context)
        self._graph_metrics.record_projection(len(graph_projection.nodes), len(graph_projection.edges))
        await self._threat_memory.remember(graph_projection)
        await self._emit_graph_events(request, graph_projection)
        threat_correlation = await self._threat_correlation_engine.correlate(graph_projection)
        await self._emit_correlation_events(request, threat_correlation.model_dump(mode="json"))

        await self._publish(request, EventName.INVESTIGATION_PROGRESS, {"message": "Calculating risk profile"})
        threat_score = await self._scoring_engine.score(request.investigation_id, results)
        await self._investigation_repository.save_verdict(request.investigation_id, threat_score)
        if threat_score.severity in {ThreatSeverity.HIGH, ThreatSeverity.CRITICAL}:
            await self._publish(request, EventName.THREAT_DETECTED, threat_score.model_dump(mode="json"))

        evidence = self._evidence_from_results(results)
        report = self._report_builder.build(context, threat_score, evidence)
        
        # Get active provider from metrics
        active_provider, active_model = self._provider_metrics.get_active_provider()
        
        result = InvestigationResult(
            investigation_id=request.investigation_id,
            correlation_id=request.correlation_id,
            finding=InvestigationFinding(
                summary=report.summary,
                risk_level=self._risk_level(threat_score),
                evidence=report.evidence,
                recommended_actions=[
                    "Review evidence before taking enforcement action.",
                    "Preserve original artifacts for sandbox analysis.",
                ],
            ),
            active_provider=active_provider,
            active_model=active_model,
        )
        await self._publish(
            request,
            EventName.INVESTIGATION_COMPLETED,
            {"risk_level": result.finding.risk_level.value, "score": threat_score.final_score},
        )
        self._graph_metrics.record_workflow_latency(int((perf_counter() - workflow_started) * 1000))
        await self._session_memory.remove(request.investigation_id)
        return result

    async def _emit_graph_events(self, request: InvestigationRequest, projection) -> None:
        for node in projection.nodes:
            if node.id != request.investigation_id:
                await self._publish(request, EventName.GRAPH_NODE_ADDED, node.model_dump(mode="json"))
        for edge in projection.edges:
            await self._publish(request, EventName.GRAPH_EDGE_ADDED, edge.model_dump(mode="json"))

    async def _emit_correlation_events(self, request: InvestigationRequest, payload: dict) -> None:
        if payload.get("related_investigations"):
            await self._publish(request, EventName.ENTITY_CORRELATED, payload)
        for campaign in payload.get("campaign_detections", []):
            self._graph_metrics.record_campaign()
            await self._publish(request, EventName.CAMPAIGN_DETECTED, campaign)

    async def _run_agent(self, agent_name: str, request: InvestigationRequest) -> AgentResult | None:
        agent = self._agents.get(agent_name)
        if agent is None:
            await self._publish(request, EventName.AGENT_FAILED, {"agent": agent_name, "error": "not_registered"})
            return None
        await self._publish(request, EventName.AGENT_STARTED, {}, agent=agent.name)
        started = perf_counter()
        try:
            async with asyncio.timeout(self._agent_timeout_seconds):
                result = await agent.run(request, AgentContext(self._event_bus))
        except Exception as error:
            duration_ms = int((perf_counter() - started) * 1000)
            self._agent_metrics.record(AgentTrace(request.investigation_id, agent.name, duration_ms, False))
            await self._publish(
                request,
                EventName.AGENT_FAILED,
                {"duration_ms": duration_ms, "error": str(error)},
                agent=agent.name,
            )
            raise
        duration_ms = int((perf_counter() - started) * 1000)
        self._agent_metrics.record(AgentTrace(request.investigation_id, agent.name, duration_ms, True))
        provider = getattr(result, "provider", None)
        if isinstance(provider, str) and provider in {"nvidia_nim", "openai", "pollinations"}:
            self._provider_metrics.record(
                ProviderTrace(
                    investigation_id=request.investigation_id,
                    request_id=f"{request.investigation_id}:{agent.name}",
                    provider=provider,
                    operation=agent.name,
                    latency_ms=duration_ms,
                    success=True,
                )
            )
        await self._publish(request, EventName.AGENT_COMPLETED, {"duration_ms": duration_ms}, agent=agent.name)
        return result

    async def _publish(
        self,
        request: InvestigationRequest,
        event: EventName,
        payload: dict,
        agent: str | None = None,
    ) -> None:
        envelope = EventEnvelope(
            event=event,
            correlation_id=request.correlation_id,
            agent=agent,
            payload={"investigation_id": request.investigation_id, **payload},
        )
        await self._event_bus.publish(envelope)

    def _risk_level(self, threat_score: ThreatScore) -> RiskLevel:
        return {
            ThreatSeverity.LOW: RiskLevel.LOW,
            ThreatSeverity.MEDIUM: RiskLevel.MEDIUM,
            ThreatSeverity.HIGH: RiskLevel.HIGH,
            ThreatSeverity.CRITICAL: RiskLevel.CRITICAL,
        }[threat_score.severity]

    def _evidence_from_results(self, results: list[AgentResult]) -> list[EvidenceItem]:
        evidence: list[EvidenceItem] = []
        for result in results:
            if isinstance(result, BehaviorResult):
                evidence.append(EvidenceItem(label="Behavior analysis", detail=result.explanation, confidence=result.confidence))
            elif isinstance(result, OSINTResult):
                detail = ", ".join(result.suspicious_indicators) or "No suspicious OSINT indicator found."
                evidence.append(EvidenceItem(label="OSINT analysis", detail=detail, confidence=result.confidence))
            elif isinstance(result, VisionResult):
                detail = ", ".join(result.suspicious_elements) or "No suspicious visual element found."
                evidence.append(EvidenceItem(label="Vision analysis", detail=detail, confidence=result.confidence))
            elif isinstance(result, AudioResult):
                detail = ", ".join(result.detected_patterns) or result.summary or "No suspicious audio pattern found."
                evidence.append(EvidenceItem(label="Audio analysis", detail=detail, confidence=result.confidence))
            elif isinstance(result, WebSearchResult):
                verified = ", ".join(result.verified_entities) or "None confirmed"
                unverified = ", ".join(result.unverified_entities) or "None"
                delta_str = f"Score adjusted {result.trust_delta:+d}" if result.trust_delta != 0 else "No adjustment"
                detail = f"Verified: {verified}. Unverified: {unverified}. {delta_str}."
                if result.web_summary:
                    detail += f" {result.web_summary}"
                evidence.append(EvidenceItem(
                    label="Web verification",
                    detail=detail[:500],
                    confidence=0.90 if result.search_performed else 0.70,
                ))
        return evidence
