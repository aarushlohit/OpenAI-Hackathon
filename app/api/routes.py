from fastapi import APIRouter, Request

from app.schemas.investigation import InvestigationRequest, InvestigationResult

router = APIRouter(prefix="/v1")


@router.post("/investigations", response_model=InvestigationResult)
async def create_investigation(payload: InvestigationRequest, request: Request) -> InvestigationResult:
    return await request.app.state.container.orchestrator.investigate(payload)


@router.post("/investigate", response_model=InvestigationResult)
async def investigate_alias(payload: InvestigationRequest, request: Request) -> InvestigationResult:
    return await create_investigation(payload, request)

@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/observability/provider-metrics")
async def provider_metrics(request: Request) -> dict[str, dict[str, float | int]]:
    return request.app.state.container.provider_metrics.snapshot()


@router.get("/observability/agent-metrics")
async def agent_metrics(request: Request) -> dict[str, dict[str, float | int]]:
    return request.app.state.container.agent_metrics.snapshot()


@router.get("/observability/graph-metrics")
async def graph_metrics(request: Request) -> dict[str, int]:
    return request.app.state.container.graph_metrics.snapshot()


@router.get("/observability/runtime-metrics")
async def runtime_metrics(request: Request) -> dict:
    return request.app.state.container.runtime_metrics.snapshot().model_dump(mode="json")


@router.get("/providers/capabilities")
async def provider_capabilities(request: Request) -> dict:
    return request.app.state.container.provider_capabilities.snapshot()


@router.get("/threat-feed")
async def threat_feed(request: Request) -> list[dict]:
    items = await request.app.state.container.threat_feed.latest()
    return [item.model_dump(mode="json") for item in items]


@router.get("/demo/scenarios")
async def demo_scenarios(request: Request) -> list[dict]:
    return [scenario.model_dump(mode="json") for scenario in request.app.state.container.demo_scenarios.list()]


@router.get("/workflows")
async def workflows(request: Request) -> list[dict]:
    return [workflow.model_dump(mode="json") for workflow in request.app.state.container.workflow_registry.list()]


@router.get("/investigations/{investigation_id}/events")
async def investigation_events(investigation_id: str, request: Request) -> list[dict]:
    events = await request.app.state.container.investigation_repository.list_events(investigation_id)
    return [event.safe_payload() for event in events]


@router.get("/investigations/{investigation_id}/replay")
async def investigation_replay(investigation_id: str, request: Request) -> dict:
    session = await request.app.state.container.replay_engine.build(investigation_id)
    if request.app.state.container.replay_engine.verify(session):
        request.app.state.container.graph_metrics.record_replay_verification()
    return session.model_dump(mode="json")


@router.get("/investigations/{investigation_id}/context")
async def investigation_context(investigation_id: str, request: Request) -> dict:
    context = await request.app.state.container.investigation_repository.load_context(investigation_id)
    return {} if context is None else context.model_dump(mode="json")
