from app.orchestrator.workflow_registry import WorkflowRegistry
from app.orchestrator.workflows import WorkflowDefinition
from app.schemas.investigation import InvestigationRequest


class PipelineRouter:
    def __init__(self, workflow_registry: WorkflowRegistry) -> None:
        self._workflow_registry = workflow_registry

    def route(self, request: InvestigationRequest) -> WorkflowDefinition:
        return self._workflow_registry.select(request.kind)

