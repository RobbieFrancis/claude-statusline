#!/usr/bin/env python3
"""
Claude Statusline Configurator - Terminal TUI for configuring the statusline.

Requires: pip3 install textual
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Switch, Input, Button, Label, Footer, Header
from textual.binding import Binding
from pathlib import Path
import json


class StatuslinePreview(Static):
    """Widget that displays a live preview of the statusline."""

    def update_preview(self, config: dict):
        """Update the preview based on current config."""
        preview = self._generate_preview(config)
        self.update(preview)

    def _generate_preview(self, config: dict) -> str:
        """Generate preview output matching statusline.py logic using Rich markup."""
        parts = []

        if config.get("show_title"):
            title = config.get("title", "Statusline_Pro")
            parts.append(f"[bold white]{title}[/]")

        if config.get("show_model"):
            parts.append("[cyan]Opus 4.5[/]")

        if config.get("show_project"):
            parts.append("[yellow]my-project[/]")

        if config.get("show_git_branch"):
            branch_part = "[green]main[/]"
            if config.get("show_git_status"):
                branch_part += " [yellow]*3 (+1,~2)[/]"
            if config.get("show_git_ahead_behind"):
                branch_part += " [green]↑2[/] [red]↓1[/]"
            parts.append(branch_part)

        if config.get("show_context_bar"):
            bar = "███░░░░░░░░░░░░░░░░░"
            parts.append(f"[magenta]15% [{bar}] 30K/200K tokens[/]")

        if config.get("show_usage_limits"):
            parts.append("[red]5h: 45% / 7d: 23%[/]")

        if config.get("show_session_duration"):
            parts.append("[cyan]1h 23m[/]")

        if config.get("show_message_count"):
            parts.append("[blue]42 msgs[/]")

        separator = " [dim]|[/] "
        return separator.join(parts) if parts else "[dim italic]No options enabled[/]"


class StatuslineConfigurator(App):
    """TUI application for configuring the Claude statusline."""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        padding: 1 2;
    }

    #title-section {
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $primary;
    }

    #title-section Label {
        margin-bottom: 1;
    }

    #title-input {
        width: 100%;
    }

    #options-section {
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $secondary;
    }

    #options-section > Label {
        margin-bottom: 1;
        text-style: bold;
    }

    .options-grid {
        layout: grid;
        grid-size: 2;
        grid-gutter: 1;
        height: auto;
    }

    .option-row {
        height: auto;
        width: 100%;
    }

    .option-row Switch {
        margin-right: 1;
    }

    #preview-section {
        height: auto;
        padding: 1;
        margin-bottom: 1;
        border: solid $success;
    }

    #preview-section > Label {
        margin-bottom: 1;
        text-style: bold;
    }

    #preview {
        padding: 1;
        background: $panel;
    }

    #button-section {
        height: auto;
        align: center middle;
        padding: 1;
    }

    #button-section Button {
        margin: 0 2;
    }

    #save-btn {
        background: $success;
    }
    """

    BINDINGS = [
        Binding("s", "save", "Save", show=True),
        Binding("escape", "cancel", "Cancel", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.config_path = Path.home() / ".claude" / "statusline-config.json"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load config from file or use defaults."""
        default_config = {
            "title": "Statusline_Pro",
            "show_title": True,
            "show_usage_limits": False,
            "show_git_branch": True,
            "show_git_status": True,
            "show_git_ahead_behind": True,
            "show_context_bar": True,
            "show_model": True,
            "show_project": True,
            "show_message_count": True,
            "show_session_duration": True,
        }

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except (json.JSONDecodeError, IOError):
                pass

        return default_config

    def _save_config(self):
        """Save config to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)
        f.write("\n")

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="main-container"):
            # Title input section
            with Container(id="title-section"):
                yield Label("Statusline Title")
                yield Input(
                    value=self.config.get("title", "Statusline_Pro"),
                    placeholder="Enter statusline title",
                    id="title-input"
                )

            # Boolean options section
            with Container(id="options-section"):
                yield Label("Display Options")

                options = [
                    ("show_title", "Show Title"),
                    ("show_model", "Show Model"),
                    ("show_project", "Show Project"),
                    ("show_git_branch", "Show Git Branch"),
                    ("show_git_status", "Show Git Status"),
                    ("show_git_ahead_behind", "Show Ahead/Behind"),
                    ("show_context_bar", "Show Context Bar"),
                    ("show_usage_limits", "Show Usage Limits"),
                    ("show_session_duration", "Show Session Duration"),
                    ("show_message_count", "Show Message Count"),
                ]

                with Container(classes="options-grid"):
                    for key, label in options:
                        with Horizontal(classes="option-row"):
                            yield Switch(
                                value=self.config.get(key, True),
                                id=f"switch_{key}"
                            )
                            yield Label(label)

            # Preview section
            with Container(id="preview-section"):
                yield Label("Live Preview")
                yield StatuslinePreview(id="preview")

            # Buttons
            with Horizontal(id="button-section"):
                yield Button("Save", variant="success", id="save-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

        yield Footer()

    def on_mount(self):
        """Called when app is mounted."""
        self.title = "Claude Statusline Configurator"
        self._update_preview()

    def on_switch_changed(self, event: Switch.Changed):
        """Handle switch toggle events."""
        switch_id = event.switch.id
        if switch_id and switch_id.startswith("switch_"):
            key = switch_id.replace("switch_", "")
            self.config[key] = event.value
            self._update_preview()

    def on_input_changed(self, event: Input.Changed):
        """Handle title input changes."""
        if event.input.id == "title-input":
            self.config["title"] = event.value
            self._update_preview()

    def _update_preview(self):
        """Update the preview widget."""
        preview = self.query_one("#preview", StatuslinePreview)
        preview.update_preview(self.config)

    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        if event.button.id == "save-btn":
            self.action_save()
        elif event.button.id == "cancel-btn":
            self.action_cancel()

    def action_save(self):
        """Save configuration and exit."""
        self._save_config()
        self.exit(message="Configuration saved! Changes will appear on next statusline refresh.")

    def action_cancel(self):
        """Exit without saving."""
        self.exit(message="Cancelled - no changes saved.")

    def action_quit(self):
        """Quit the application."""
        self.exit()


def main():
    """Entry point for the configurator."""
    try:
        from textual import __version__
    except ImportError:
        print("Error: The 'textual' library is required.")
        print("Install it with: pip3 install textual")
        return 1

    app = StatuslineConfigurator()
    result = app.run()
    if result:
        print(result)
    return 0


if __name__ == "__main__":
    exit(main())
