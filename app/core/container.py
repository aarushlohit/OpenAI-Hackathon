from app.agents.behavior import BehaviorAnalysisAgent
from app.agents.intake_agent import IntakeAgent
from app.agents.osint import OSINTAgent
from app.agents.vision import VisionAnalysisAgent
from app.core.config import get_settings
from app.events.bus import InMemoryEventBus
from app.gateway.audio_router import AudioRouter
from app.gateway.capabilities import ProviderModality, default_capability_registry
from app.gateway.embedding_router import EmbeddingRouter
from app.gateway.multimodal_router import MultimodalRouter
from app.gateway.provider_priority import ProviderPriorityResolver
from app.gateway.providers.nvidia_nim_provider import NvidiaNimProvider
from app.gateway.providers.openai_provider import OpenAIProvider
from app.gateway.providers.pollinations_provider import PollinationsProvider
from app.gateway.router_core import FailoverRouter
from app.gateway.text_router import TextRouter
from app.gateway.vision_router import VisionRouter
from app.graph import ThreatGraphEngine
from app.graph.repositories import InMemoryGraphRepository
from app.memory.repository import InMemoryMemoryRepository, MemoryRepository
from app.memory.context_snapshots import ContextSnapshotStore
from app.memory.entity_index import EntityIndex
from app.memory.investigation_repository import InMemoryInvestigationRepository
from app.memory.session_memory import SessionMemory
from app.memory.threat_memory import ThreatMemory
from app.observability import AgentMetrics, CircuitBreaker, GraphMetrics, ProviderMetrics
from app.orchestrator import InvestigationEngine
from app.orchestrator.context_manager import InvestigationContextManager
from app.orchestrator.pipeline_router import PipelineRouter
from app.orchestrator.workflow_registry import WorkflowRegistry
from app.prompts import PromptRegistry
from app.extraction import EntityExtractor
from app.intelligence import CampaignDetector, ReputationCorrelationEngine, ThreatCorrelationEngine
from app.reporting import ReportBuilder
from app.replay import ReplayEngine
from app.scoring import ThreatScoringEngine
from app.security.input_policy import IntakePolicy
from app.services.ocr import SafeOCRService
from app.services.reputation import DomainReputationService
from app.services.scam_lookup import ScamLookupService
from app.services.whois import WhoisService
from app.websocket.manager import WebsocketConnectionManager
from app.autonomous import AutonomousMonitorEngine
from app.autonomous.alerting import EscalationRules
from app.autonomous.watchers import EntityWatcher
from app.demo import CinemaMode, DemoScenarioRegistry
from app.intelligence import ThreatFeed
from app.governance import AgentContractRegistry, GovernancePolicy
from app.contracts import SchemaRegistry
from app.replay import ReplayDeterminismVerifier
from app.evaluation import BenchmarkRunner
from pathlib import Path
from app.runtime import RedisRuntime, RuntimeBootstrap, RuntimeHealthManager
from app.runtime.redis_client_factory import create_redis_client
from app.events.dead_letter_queue import DeadLetterQueue
from app.events.redis_broadcast import RedisEventBroadcaster
from app.replay import SnapshotBuilder, SnapshotValidator
from app.diagnostics import ReplayAnalyzer
from app.observability import RuntimeMetrics


class AppContainer:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.event_bus = InMemoryEventBus(max_size=self.settings.event_stream_buffer_size)
        self.websocket_manager = WebsocketConnectionManager(self.event_bus)
        self.dead_letter_queue = DeadLetterQueue()
        self.redis_runtime = RedisRuntime(create_redis_client(self.settings.redis_dsn))
        self.redis_broadcaster = RedisEventBroadcaster(self.redis_runtime)
        self.runtime_metrics = RuntimeMetrics()
        self.runtime_health = RuntimeHealthManager()
        self.memory_repository: MemoryRepository = InMemoryMemoryRepository()
        self.investigation_repository = InMemoryInvestigationRepository()
        self.replay_engine = ReplayEngine(self.investigation_repository)
        self.replay_verifier = ReplayDeterminismVerifier(self.replay_engine)
        self.snapshot_builder = SnapshotBuilder()
        self.snapshot_validator = SnapshotValidator()
        self.replay_analyzer = ReplayAnalyzer()
        self.graph_repository = InMemoryGraphRepository()
        self.threat_graph_engine = ThreatGraphEngine(self.graph_repository)
        self.entity_index = EntityIndex()
        self.threat_memory = ThreatMemory(self.entity_index)
        self.threat_correlation_engine = ThreatCorrelationEngine(
            self.graph_repository,
            CampaignDetector(),
        )
        self.event_bus.add_recorder(self._record_event)
        self.event_bus.add_recorder(self._broadcast_event)
        self.session_memory = SessionMemory()
        self.snapshot_store = ContextSnapshotStore()
        self.provider_metrics = ProviderMetrics()
        self.agent_metrics = AgentMetrics()
        self.graph_metrics = GraphMetrics()
        self.threat_feed = ThreatFeed()
        self.autonomous_monitor = AutonomousMonitorEngine(
            watcher=EntityWatcher(self.threat_memory),
            escalation_rules=EscalationRules(),
            event_bus=self.event_bus,
            threat_feed=self.threat_feed,
        )
        self.demo_scenarios = DemoScenarioRegistry()
        self.cinema_mode = CinemaMode(self.event_bus)
        self.prompt_registry = PromptRegistry()
        self.schema_registry = SchemaRegistry()
        self.agent_contracts = AgentContractRegistry()
        contract_path = Path("AGENT_CONTRACT.yaml")
        if contract_path.exists():
            self.agent_contracts.load_yaml(contract_path)
        self.governance_policy = GovernancePolicy(self.agent_contracts)
        self.runtime_bootstrap = RuntimeBootstrap(
            schema_registry=self.schema_registry,
            agent_contracts=self.agent_contracts,
            websocket_manager=self.websocket_manager,
            redis_runtime=self.redis_runtime,
        )
        self.benchmark_runner = BenchmarkRunner()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.settings.provider_circuit_failure_threshold,
            recovery_seconds=self.settings.provider_circuit_recovery_seconds,
        )
        self.failover_router = FailoverRouter(
            event_bus=self.event_bus,
            circuit_breaker=self.circuit_breaker,
            metrics=self.provider_metrics,
            max_retries=self.settings.ai_max_retries,
        )

        openai = OpenAIProvider(self.settings)
        nvidia = NvidiaNimProvider(self.settings)
        pollinations = PollinationsProvider(self.settings)
        self.provider_capabilities = default_capability_registry()
        self.provider_priority = ProviderPriorityResolver(self.settings, self.provider_capabilities)
        providers = [openai, nvidia, pollinations]
        self.text_router = TextRouter(
            providers=self.provider_priority.order(ProviderModality.TEXT, providers),
            router=self.failover_router,
        )
        self.vision_router = VisionRouter(
            providers=self.provider_priority.order(ProviderModality.VISION, providers),
            router=self.failover_router,
        )
        self.audio_router = AudioRouter(
            providers=self.provider_priority.order(ProviderModality.AUDIO, providers),
            router=self.failover_router,
        )
        self.embedding_router = EmbeddingRouter(
            providers=self.provider_priority.order(ProviderModality.EMBEDDINGS, providers),
            router=self.failover_router,
        )
        self.multimodal_router = MultimodalRouter(
            self.text_router,
            self.vision_router,
            self.audio_router,
            self.embedding_router,
        )
        self.workflow_registry = WorkflowRegistry()
        self.pipeline_router = PipelineRouter(self.workflow_registry)
        self.context_manager = InvestigationContextManager(EntityExtractor())
        self.orchestrator = InvestigationEngine(
            agents=[
                IntakeAgent(IntakePolicy()),
                BehaviorAnalysisAgent(self.prompt_registry),
                OSINTAgent(
                    whois_service=WhoisService(),
                    reputation_service=DomainReputationService(),
                    scam_lookup_service=ScamLookupService(),
                    prompt_registry=self.prompt_registry,
                ),
                VisionAnalysisAgent(
                    ocr_service=SafeOCRService(),
                    prompt_registry=self.prompt_registry,
                ),
            ],
            event_bus=self.event_bus,
            pipeline_router=self.pipeline_router,
            context_manager=self.context_manager,
            investigation_repository=self.investigation_repository,
            session_memory=self.session_memory,
            snapshot_store=self.snapshot_store,
            scoring_engine=ThreatScoringEngine(),
            correlation_engine=ReputationCorrelationEngine(),
            threat_graph_engine=self.threat_graph_engine,
            threat_correlation_engine=self.threat_correlation_engine,
            threat_memory=self.threat_memory,
            report_builder=ReportBuilder(),
            agent_metrics=self.agent_metrics,
            graph_metrics=self.graph_metrics,
            agent_timeout_seconds=self.settings.agent_timeout_seconds,
        )

    async def _record_event(self, event) -> None:
        investigation_id = event.payload.get("investigation_id")
        if isinstance(investigation_id, str):
            await self.investigation_repository.append_event(investigation_id, event)

    async def _broadcast_event(self, event) -> None:
        try:
            published = await self.redis_broadcaster.publish(event)
            self.runtime_metrics.increment("redis_publishes", published)
        except Exception:
            self.runtime_metrics.increment("redis_publish_failures")
