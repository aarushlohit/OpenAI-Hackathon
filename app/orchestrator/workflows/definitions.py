from pydantic import BaseModel, Field

from app.schemas.investigation import InvestigationInputKind


class WorkflowDefinition(BaseModel):
    name: str = Field(min_length=1)
    input_kinds: set[InvestigationInputKind]
    required_agents: list[str] = Field(default_factory=list)
    parallel_agents: list[str] = Field(default_factory=list)
    description: str = Field(min_length=1)


def default_workflows() -> list[WorkflowDefinition]:
    return [
        WorkflowDefinition(
            name="url_intelligence",
            input_kinds={InvestigationInputKind.URL},
            required_agents=["intake"],
            parallel_agents=["behavior", "osint"],
            description="URL-centric investigation with behavior and infrastructure intelligence.",
        ),
        WorkflowDefinition(
            name="screenshot_intelligence",
            input_kinds={InvestigationInputKind.IMAGE_REFERENCE},
            required_agents=["intake"],
            parallel_agents=["vision", "behavior"],
            description="OCR-first screenshot investigation.",
        ),
        WorkflowDefinition(
            name="document_intelligence",
            input_kinds={InvestigationInputKind.DOCUMENT_REFERENCE},
            required_agents=["intake"],
            parallel_agents=["vision", "behavior"],
            description="Offer-letter and artifact investigation.",
        ),
        WorkflowDefinition(
            name="message_intelligence",
            input_kinds={InvestigationInputKind.TEXT},
            required_agents=["intake"],
            parallel_agents=["behavior", "osint", "vision"],
            description="Text and mixed-evidence investigation.",
        ),
    ]

