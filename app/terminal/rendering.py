import json

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.text import Text

from app.events.models import EventEnvelope, EventName
from app.schemas.investigation import InvestigationResult


class TerminalRenderer:
    def __init__(self, console: Console) -> None:
        self._console = console

    def header(self) -> None:
        title = Text("HERMES-X // COGNITIVE DEFENSE TERMINAL", style="bold cyan")
        self._console.print(Panel(title, border_style="cyan"))

    def event(self, envelope: EventEnvelope) -> None:
        if envelope.event in {EventName.INVESTIGATION_STARTED, EventName.INVESTIGATION_PROGRESS}:
            self._orchestrator_event(envelope)
            return
        if envelope.event in {EventName.AGENT_STARTED, EventName.AGENT_PROGRESS, EventName.AGENT_COMPLETED}:
            self._agent_event(envelope)
            return
        if envelope.event == EventName.AGENT_FAILED:
            self._agent_failure(envelope)
            return
        if envelope.event == EventName.THREAT_DETECTED:
            self._threat_event(envelope)
            return
        agent = f" ({escape(envelope.agent)})" if envelope.agent else ""
        payload = escape(json.dumps(envelope.payload, default=str))
        self._console.print(
            f"[dim]{envelope.timestamp.isoformat()}[/dim] "
            f"[bold magenta]{envelope.event}[/bold magenta]{agent} "
            f"[green]{payload}[/green]"
        )

    def _agent_event(self, envelope: EventEnvelope) -> None:
        agent = escape(envelope.agent or "system").title()
        message = envelope.payload.get("message")
        if envelope.event == EventName.AGENT_STARTED:
            body = "Agent online. Beginning analysis."
        elif envelope.event == EventName.AGENT_COMPLETED:
            body = f"Completed in {envelope.payload.get('duration_ms', 0)} ms."
        else:
            body = str(message or "Progress update received.")
        self._console.print(Panel(escape(body), title=f"{agent} Agent", border_style="cyan"))

    def _agent_failure(self, envelope: EventEnvelope) -> None:
        agent = escape(envelope.agent or envelope.payload.get("agent", "unknown")).title()
        error = escape(str(envelope.payload.get("error", "agent failed")))
        self._console.print(Panel(error, title=f"{agent} Warning", border_style="yellow"))

    def _orchestrator_event(self, envelope: EventEnvelope) -> None:
        if envelope.event == EventName.INVESTIGATION_STARTED:
            body = f"Workflow selected: {envelope.payload.get('workflow', 'unknown')}"
        else:
            body = str(envelope.payload.get("message") or envelope.payload.get("warning") or "Progress update")
        self._console.print(Panel(escape(body), title="Orchestrator", border_style="magenta"))

    def _threat_event(self, envelope: EventEnvelope) -> None:
        score = envelope.payload.get("final_score", envelope.payload.get("score", 0))
        severity = envelope.payload.get("severity", "unknown")
        factors = ", ".join(envelope.payload.get("contributing_factors", []))
        self._console.print(
            Panel(
                escape(f"Severity: {severity}\nScore: {score}\nFactors: {factors}"),
                title="Threat Alert",
                border_style="red",
            )
        )

    def result(self, result: InvestigationResult) -> None:
        finding = result.finding
        verdict = f"{finding.risk_level.value.upper()} RISK - {finding.summary}"
        provider_info = ""
        if result.active_provider:
            provider_info = f"\n[bold]Primary Cognition:[/bold] {result.active_provider}"
            if result.active_model:
                provider_info += f" ({result.active_model})"
        self._console.print(
            Panel(
                f"[bold]Investigation:[/bold] {result.investigation_id}\n"
                f"[bold]Risk:[/bold] {finding.risk_level}\n"
                f"[bold]Final Verdict:[/bold] {escape(verdict)}\n"
                f"[bold]Actions:[/bold] {', '.join(finding.recommended_actions)}"
                f"{provider_info}",
                title="Investigation Result",
                border_style="green",
            )
        )
