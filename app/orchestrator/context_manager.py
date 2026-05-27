from app.extraction import EntityExtractor
from app.models.investigation_context import InvestigationContext
from app.schemas.investigation import InvestigationRequest


class InvestigationContextManager:
    def __init__(self, extractor: EntityExtractor) -> None:
        self._extractor = extractor

    def create(self, request: InvestigationRequest) -> InvestigationContext:
        entities = self._extractor.extract(request.raw_input)
        return InvestigationContext(
            investigation_id=request.investigation_id,
            correlation_id=request.correlation_id,
            raw_input=request.raw_input,
            evidence_kind=request.kind.value,
            entities=entities,
        )

