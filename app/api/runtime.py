from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1/runtime")


@router.get("/health")
async def runtime_health(request: Request) -> dict:
    return (await request.app.state.container.runtime_health.health()).model_dump(mode="json")


@router.get("/readiness")
async def runtime_readiness(request: Request) -> dict:
    return (await request.app.state.container.runtime_health.readiness()).model_dump(mode="json")


@router.get("/liveness")
async def runtime_liveness(request: Request) -> dict:
    return (await request.app.state.container.runtime_health.liveness()).model_dump(mode="json")


@router.get("/dependencies")
async def runtime_dependencies(request: Request) -> list[dict]:
    return [status.model_dump(mode="json") for status in request.app.state.container.runtime_health.dependencies()]


@router.get("/bootstrap")
async def runtime_bootstrap(request: Request) -> dict:
    return (await request.app.state.container.runtime_bootstrap.verify()).model_dump(mode="json")
