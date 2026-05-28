#!/usr/bin/env python3
"""
TUI Launcher for Real Evidence Validation System
Provides interactive menu-driven interface for Hermes-X multimodal evidence processing
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from textual.app import ComposeResult, RenderableType
    from textual.containers import Container, Vertical, Horizontal
    from textual.widgets import Header, Footer, Static, Button, Label, Select, Input
    from textual.screen import Screen
    from textual.binding import Binding
    from textual import work
    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax
    from textual.reactive import reactive
except ImportError:
    print("⚠️  Textual not installed. Installing dependencies...\n")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "textual", "rich"],
        check=True
    )
    from textual.app import ComposeResult, RenderableType
    from textual.containers import Container, Vertical, Horizontal
    from textual.widgets import Header, Footer, Static, Button, Label, Select, Input
    from textual.screen import Screen
    from textual.binding import Binding
    from textual import work
    from rich.panel import Panel
    from rich.text import Text
    from rich.syntax import Syntax
    from textual.reactive import reactive

# Get workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent
TEST_ASSETS = WORKSPACE_ROOT / "test_assets"
VALIDATION_SCRIPT = WORKSPACE_ROOT / "scripts" / "validate_input.py"


class OutputDisplay(Static):
    """Widget to display validation output"""

    def render(self) -> RenderableType:
        return Panel(
            Text(self.app.output_text or "Ready...", style="cyan"),
            title="[bold]Validation Output[/bold]",
            border_style="blue",
            expand=True,
        )


class MainMenu(Screen):
    """Main menu screen"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "clear", "Clear Output"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("[bold cyan]🔍 Hermes-X Real Evidence Validator[/bold cyan]")
            yield Label("[yellow]Real NVIDIA Multimodal Cognition Proof System[/yellow]\n")
            yield Label("[dim]Select evidence type:[/dim]")
            
            with Horizontal():
                yield Button("📄 Text Evidence", id="text", variant="primary")
                yield Button("🖼️  Image Evidence", id="image", variant="default")
                yield Button("📑 PDF Evidence", id="pdf", variant="default")
                yield Button("🎵 Audio Evidence", id="audio", variant="default")
                yield Button("✏️ Type Text", id="type_text", variant="primary")
                yield Button("📎 Attach Image", id="attach_image", variant="primary")
            
            yield Label("")
            with Horizontal():
                yield Button("📋 Browse Assets", id="browse", variant="default")
                yield Button("⚙️  Settings", id="settings", variant="default")
                yield Button("❌ Exit", id="exit", variant="error")
            
            yield Label("\n[dim]Evidence Processing: Risk Score | Signal Detection | Consensus Analysis[/dim]")
            yield OutputDisplay(id="output")
        
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "text":
            self.app.push_screen(EvidenceSelector("text"))
        elif button_id == "image":
            self.app.show_toast("🖼️  Image support coming in Phase 5")
        elif button_id == "pdf":
            self.app.show_toast("📑 PDF support coming in Phase 5")
        elif button_id == "audio":
            self.app.show_toast("🎵 Audio support coming in Phase 5")
        elif button_id == "type_text":
            self.app.push_screen(TextInputScreen())
        elif button_id == "attach_image":
            self.app.push_screen(ImageInputScreen())
        elif button_id == "browse":
            self.app.push_screen(AssetBrowser())
        elif button_id == "settings":
            self.app.show_toast("⚙️  Settings coming soon")
        elif button_id == "exit":
            self.app.exit()

    def action_clear(self) -> None:
        self.app.output_text = ""


class EvidenceSelector(Screen):
    """Screen to select evidence file"""

    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, evidence_type: str):
        super().__init__()
        self.evidence_type = evidence_type
        self.files = []
        self.load_files()

    def load_files(self):
        """Load available test assets"""
        asset_path = TEST_ASSETS / "text"
        if asset_path.exists():
            scams = list((asset_path / "scams").glob("*.txt")) if (asset_path / "scams").exists() else []
            legit = list((asset_path / "legitimate").glob("*.txt")) if (asset_path / "legitimate").exists() else []
            self.files = [
                ("📛 SCAMS", scams),
                ("✅ LEGITIMATE", legit),
            ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label(f"[bold cyan]Select {self.evidence_type.upper()} Evidence[/bold cyan]\n")
            
            for category, files in self.files:
                if files:
                    yield Label(f"[yellow]{category}[/yellow]")
                    with Horizontal():
                        for f in files:
                            yield Button(f"  {f.stem}", id=str(f), variant="primary")
                    yield Label("")
            
            yield Button("← Back", id="back", variant="error")
        
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.app.pop_screen()
        else:
            # Run validation on selected file
            self.app.validate_file(button_id, self.evidence_type)
            self.app.pop_screen()

    def action_back(self) -> None:
        self.app.pop_screen()


class TextInputScreen(Screen):
    BINDINGS = [Binding("b", "back", "Back"), Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("[bold cyan]Type Text Evidence[/bold cyan]\n")
            yield Input(placeholder="Paste text here and press Enter", id="text_input")
            yield Button("Submit", id="submit_text", variant="primary")
            yield Button("← Back", id="back", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "submit_text":
            val = self.query_one("#text_input", Input).value
            if val and val.strip():
                tmp = Path("/tmp/harmless_input.txt")
                tmp.write_text(val)
                self.app.validate_file(str(tmp), "text")
                self.app.pop_screen()


class ImageInputScreen(Screen):
    BINDINGS = [Binding("b", "back", "Back"), Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("[bold cyan]Attach Image Evidence[/bold cyan]\n")
            yield Input(placeholder="Path to image file (e.g. test_assets/images/example.png)", id="img_input")
            yield Button("Submit", id="submit_img", variant="primary")
            yield Button("← Back", id="back", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "submit_img":
            fp = self.query_one("#img_input", Input).value
            if fp and Path(fp).exists():
                self.app.validate_file(fp, "image")
                self.app.pop_screen()
            else:
                self.app.show_toast("File not found")


class AssetBrowser(Screen):
    """Browse test assets"""

    BINDINGS = [
        Binding("b", "back", "Back"),
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical():
            yield Label("[bold cyan]📂 Test Assets Browser[/bold cyan]\n")
            
            # Show directory structure
            yield Label("[yellow]test_assets/[/yellow]")
            yield Label("├── text/")
            yield Label("│   ├── scams/")
            yield Label("│   │   └── telegram_recruitment_scam.txt (826 B)")
            yield Label("│   └── legitimate/")
            yield Label("│       └── google_offer_notification.txt (973 B)")
            yield Label("├── images/ (Phase 5)")
            yield Label("├── pdfs/ (Phase 5)")
            yield Label("└── audio/ (Phase 5)\n")
            
            yield Label("[cyan]Ready for expansion:[/cyan]")
            yield Label("• OCR + Vision model integration")
            yield Label("• Document forensics (PDF metadata)")
            yield Label("• Audio transcription + tone analysis")
            
            yield Button("← Back", id="back", variant="error")
        
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.pop_screen()

    def action_back(self) -> None:
        self.app.pop_screen()


class ValidationApp:
    """Main TUI Application"""

    output_text = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

    async def validate_file(self, filepath: str, evidence_type: str):
        """Execute validation on selected file"""
        self.output_text = f"🔄 Validating {evidence_type} evidence...\n"
        self.screen.query_one("#output", OutputDisplay).refresh()
        
        await self._run_validation(filepath, evidence_type)

    @work(exclusive=True)
    async def _run_validation(self, filepath: str, evidence_type: str):
        """Run validation in background"""
        try:
            cmd = [
                sys.executable,
                str(VALIDATION_SCRIPT),
                f"--{evidence_type}",
                filepath,
                "--json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse and display results
                output_lines = result.stdout.split('\n')
                
                # Show validation trace
                self.output_text = "[cyan]" + "[/cyan]\n[cyan]".join(
                    [line for line in output_lines if line.strip()][:30]
                ) + "[/cyan]"
                
                # Try to parse JSON for summary
                try:
                    json_output = None
                    for line in output_lines:
                        if line.strip().startswith('{'):
                            json_output = json.loads(line)
                            break
                    
                    if json_output and 'investigation' in json_output:
                        inv = json_output['investigation']
                        self.output_text += f"\n\n[bold green]✅ VALIDATION PASSED[/bold green]\n"
                        self.output_text += f"Risk Score: [yellow]{inv.get('risk_score', 'N/A')}/100[/yellow]\n"
                        self.output_text += f"Confidence: [cyan]{inv.get('confidence', 'N/A'):.0%}[/cyan]\n"
                        self.output_text += f"Severity: [bold]{inv.get('severity', 'N/A')}[/bold]\n"
                        self.output_text += f"Model: [magenta]{inv.get('provider_model', 'NVIDIA Nemotron').split('/')[-1]}[/magenta]"
                except json.JSONDecodeError:
                    pass
            else:
                self.output_text = f"[red]❌ Validation failed:\n{result.stderr}[/red]"
            
            self.screen.query_one("#output", OutputDisplay).refresh()
        
        except Exception as e:
            self.output_text = f"[red]❌ Error: {str(e)}[/red]"


# Create TUI using raw terminal since textual needs full app structure
def run_tui():
    """Run the TUI launcher"""
    from textual.app import App
    
    class HermesValidatorApp(App):
        """Hermes-X Validator TUI"""
        
        TITLE = "Hermes-X Real Evidence Validator"
        SUB_TITLE = "NVIDIA Multimodal Cognition Proof System"
        
        def __init__(self):
            super().__init__()
            self.output_text = ""
        
        def on_mount(self) -> None:
            self.push_screen(MainMenu())
        
        def validate_file(self, filepath: str, evidence_type: str):
            """Execute validation"""
            self.run_worker(self._run_validation_worker(filepath, evidence_type), exclusive=True)
        
        async def _run_validation_worker(self, filepath: str, evidence_type: str):
            """Background validation worker"""
            try:
                self.output_text = f"🔄 Validating {evidence_type} evidence...\n"
                
                cmd = [
                    sys.executable,
                    str(VALIDATION_SCRIPT),
                    f"--{evidence_type}",
                    filepath,
                    "--json"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    output_lines = result.stdout.split('\n')
                    display_lines = [line for line in output_lines if line.strip()][:35]
                    self.output_text = "\n".join(display_lines)
                    
                    # Extract JSON for quick summary
                    for line in output_lines:
                        if line.strip().startswith('{'):
                            try:
                                json_data = json.loads(line)
                                if 'investigation' in json_data:
                                    inv = json_data['investigation']
                                    self.output_text += f"\n\n[bold green]✅ Complete[/bold green]\n"
                                    self.output_text += f"Risk: [yellow]{inv.get('risk_score')}/100[/yellow] | "
                                    self.output_text += f"Confidence: [cyan]{inv.get('confidence')*100:.0f}%[/cyan] | "
                                    self.output_text += f"Severity: [bold]{inv.get('severity')}[/bold]"
                                break
                            except:
                                pass
                else:
                    self.output_text = f"[red]Error: {result.stderr[:500]}[/red]"
                
                # Refresh display
                try:
                    display = self.screen.query_one("#output", OutputDisplay)
                    display.refresh()
                except:
                    pass
            
            except Exception as e:
                self.output_text = f"[red]❌ {str(e)}[/red]"
    
    app = HermesValidatorApp()
    app.run()


if __name__ == "__main__":
    run_tui()
