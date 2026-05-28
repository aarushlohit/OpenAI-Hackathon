#!/usr/bin/env python3
"""Real Hermes-X TUI investigation runner.

This uses the actual AppContainer, agents, event bus, graph, replay repository,
provider client, and scoring engine. It does not create local mock signals.
"""

from __future__ import annotations

import asyncio
import json
import sys
from contextlib import suppress

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.core.container import AppContainer
from app.events.models import EventName
from app.schemas.investigation import InvestigationInputKind, InvestigationRequest

console = Console()


def read_multiline_input() -> str:
    console.print(Panel.fit("Enter evidence. Press Enter twice to run.", title="Hermes-X"))
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "" and (not lines or lines[-1] == ""):
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if not text:
        raise SystemExit("No evidence provided.")
    return text


async def stream_events(container: AppContainer, request: InvestigationRequest) -> None:
    async for event in container.event_bus.stream(request.correlation_id):
        payload = event.payload
        if event.event == EventName.INVESTIGATION_STARTED:
            console.print(f"[bold cyan][INTAKE][/bold cyan] Investigation started ({payload.get('workflow')})")
        elif event.event == EventName.AGENT_STARTED:
            console.print(f"[bold blue][{event.agent or 'agent'}][/bold blue] running")
        elif event.event == EventName.AGENT_COMPLETED:
            console.print(f"[green][{event.agent or 'agent'}][/green] completed in {payload.get('duration_ms')}ms")
        elif event.event == EventName.AGENT_FAILED:
            console.print(f"[red][{event.agent or 'agent'}][/red] failed: {payload.get('error')}")
        elif event.event == EventName.GRAPH_NODE_ADDED:
            console.print("[magenta][GRAPH][/magenta] node added")
        elif event.event == EventName.GRAPH_EDGE_ADDED:
            console.print("[magenta][GRAPH][/magenta] edge added")
        elif event.event == EventName.ENTITY_CORRELATED:
            console.print("[yellow][CONSENSUS][/yellow] cross-entity correlation detected")
        elif event.event == EventName.THREAT_DETECTED:
            console.print(f"[red][CONSENSUS][/red] threat escalated: score={payload.get('final_score')}")
        elif event.event == EventName.INVESTIGATION_COMPLETED:
            console.print(f"[bold green][REPLAY][/bold green] snapshot persisted for {payload.get('investigation_id')}")
            return


def provider_label(provider: str | None, model: str | None) -> str:
    if provider == "nvidia_nim":
        return f"NVIDIA Nemotron Omni ({model})"
    if provider == "pollinations":
        return f"Pollinations ({model})"
    if provider == "openai":
        return f"OpenAI ({model})"
    return "No active cognition runtime."


async def main() -> int:
    evidence = read_multiline_input()
    container = AppContainer()
    request = InvestigationRequest(raw_input=evidence, kind=InvestigationInputKind.TEXT)

    event_task = asyncio.create_task(stream_events(container, request))
    try:
        result = await container.orchestrator.investigate(request)
    except Exception as exc:
        event_task.cancel()
        with suppress(asyncio.CancelledError):
            await event_task
        console.print("[red][NVIDIA] Runtime unavailable[/red]")
        console.print("[red][HERMES] Investigation aborted[/red]")
        console.print(f"[red]Reason: {exc}[/red]")
        return 1

    with suppress(asyncio.TimeoutError):
        await asyncio.wait_for(event_task, timeout=2.0)

    replay = await container.replay_engine.build(result.investigation_id)
    replay_verified = container.replay_engine.verify(replay)

    table = Table(title="Final Verdict")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Risk", result.finding.risk_level.value.upper())
    table.add_row("Summary", result.finding.summary)
    table.add_row("Produced By", "Hybrid Correlation")
    table.add_row("Primary Cognition", provider_label(result.active_provider, result.active_model))
    table.add_row("Replay", "verified" if replay_verified else "not verified")
    table.add_row("Graph", "updated")
    console.print(table)

    if "--json" in sys.argv or "-j" in sys.argv:
        console.print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
