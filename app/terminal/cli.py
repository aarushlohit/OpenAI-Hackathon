import asyncio

import typer
from rich.console import Console

from app.core.container import AppContainer
from app.events.models import EventName
from app.schemas.investigation import InvestigationInputKind, InvestigationRequest
from app.terminal.rendering import TerminalRenderer

app = typer.Typer(no_args_is_help=True)
console = Console()


async def _stream_until_complete(container: AppContainer, renderer: TerminalRenderer) -> None:
    async for event in container.event_bus.stream():
        renderer.event(event)
        if event.event == EventName.INVESTIGATION_COMPLETED:
            return


async def _investigate_async(raw_input: str) -> None:
    container = AppContainer()
    renderer = TerminalRenderer(console)
    renderer.header()

    kind = InvestigationInputKind.URL if raw_input.startswith(("http://", "https://")) else InvestigationInputKind.TEXT
    request = InvestigationRequest(raw_input=raw_input, kind=kind)

    stream_task = asyncio.create_task(_stream_until_complete(container, renderer))
    result = await container.orchestrator.investigate(request)
    await stream_task
    renderer.result(result)


@app.callback()
def main() -> None:
    """Hermes-X cyber defense terminal."""


@app.command()
def investigate(input_value: str = typer.Argument(..., help="URL, text, or artifact reference to inspect.")) -> None:
    """Investigate an internship or recruitment scam signal."""
    asyncio.run(_investigate_async(input_value))
