from fastapi import APIRouter, Request

from app.api.protection_models import ProtectionLookup, build_lookup

router = APIRouter(prefix="/v1/protection")


@router.get("/domain/{domain}", response_model=ProtectionLookup)
async def domain_lookup(domain: str, request: Request) -> ProtectionLookup:
    related = await request.app.state.container.threat_memory.related_to(domain.lower())
    return build_lookup(domain.lower(), "domain", related)


@router.get("/recruiter/{email}", response_model=ProtectionLookup)
async def recruiter_lookup(email: str, request: Request) -> ProtectionLookup:
    related = await request.app.state.container.threat_memory.related_to(email.lower())
    return build_lookup(email.lower(), "recruiter_email", related)


@router.get("/telegram/{handle}", response_model=ProtectionLookup)
async def telegram_lookup(handle: str, request: Request) -> ProtectionLookup:
    normalized = handle.lstrip("@")
    related = await request.app.state.container.threat_memory.related_to(normalized)
    return build_lookup(normalized, "telegram_handle", related)


@router.get("/upi/{upi_id}", response_model=ProtectionLookup)
async def upi_lookup(upi_id: str, request: Request) -> ProtectionLookup:
    related = await request.app.state.container.threat_memory.related_to(upi_id)
    return build_lookup(upi_id, "upi", related)


@router.get("/graph/{investigation_id}")
async def graph_lookup(investigation_id: str, request: Request) -> dict:
    projection = await request.app.state.container.graph_repository.get_projection(investigation_id)
    return {} if projection is None else projection.model_dump(mode="json")


def _lookup(entity: str, entity_type: str, related: list[str]) -> ProtectionLookup:
    return build_lookup(entity, entity_type, related)
