from app.orchestrator.workflows import WorkflowDefinition, default_workflows
from app.schemas.investigation import InvestigationInputKind


class WorkflowRegistry:
    def __init__(self, workflows: list[WorkflowDefinition] | None = None) -> None:
        self._workflows = workflows or default_workflows()

    def select(self, kind: InvestigationInputKind) -> WorkflowDefinition:
        for workflow in self._workflows:
            if kind in workflow.input_kinds:
                return workflow
        return self._workflows[-1]

    def list(self) -> list[WorkflowDefinition]:
        return list(self._workflows)

