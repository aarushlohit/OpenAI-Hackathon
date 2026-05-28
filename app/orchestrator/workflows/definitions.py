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
            parallel_agents=["behavior", "osint", "web_search"],
            description="URL-centric investigation with behavior, infrastructure and web verification.",
        ),
        WorkflowDefinition(
            name="screenshot_intelligence",
            input_kinds={InvestigationInputKind.IMAGE_REFERENCE},
            required_agents=["intake"],
            parallel_agents=["vision", "web_search"],
            description="OCR-first screenshot investigation with web verification.",
        ),
        WorkflowDefinition(
            name="document_intelligence",
            input_kinds={InvestigationInputKind.DOCUMENT_REFERENCE},
            required_agents=["intake"],
            parallel_agents=["vision", "web_search"],
            description="Offer-letter and artifact investigation with web verification.",
        ),
        WorkflowDefinition(
            name="audio_intelligence",
            input_kinds={InvestigationInputKind.AUDIO_REFERENCE},
            required_agents=["intake"],
            parallel_agents=["audio_analysis", "behavior", "web_search"],
            description="Voice and audio recruitment investigation with web verification.",
        ),
        WorkflowDefinition(
            name="message_intelligence",
            input_kinds={InvestigationInputKind.TEXT},
            required_agents=["intake", "behavior"],
            parallel_agents=["osint", "web_search"],
            description="Text and mixed-evidence investigation with web domain verification.",
        ),
    ]
