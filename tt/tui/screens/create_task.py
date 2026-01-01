"""Create Task screen."""

import pyperclip
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Static

from tt.core.ids import IDGenerator


class CreateTaskScreen(Screen):
    """Screen for creating new task IDs."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("enter", "generate", "Generate"),
        ("g", "generate", "Generate"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_generator = IDGenerator()

    def compose(self) -> ComposeResult:
        """Compose the create task screen."""
        yield Header()
        yield Container(
            Static("Create Task", classes="screen-title"),
            Vertical(
                Static(
                    "[bold]Press Enter or 'g' to generate a new task ID[/bold]",
                    id="instruction",
                ),
                Static("Press Escape to go back", id="hint"),
                Static("", id="result"),
                classes="create-task-content",
            ),
            classes="screen-container",
        )
        yield Footer()

    def action_generate(self) -> None:
        """Generate a new task ID."""
        # Generate ID and create task
        task_id, task_data = self.id_generator.create_task_with_id()

        # Copy to clipboard
        try:
            pyperclip.copy(task_id)
            clipboard_status = "✓ Copied to clipboard"
        except Exception:
            clipboard_status = "⚠ Could not copy to clipboard"

        # Update result display
        result_widget = self.query_one("#result", Static)
        result_widget.update(
            f"""
[bold green]Generated: {task_id}[/bold green]
{clipboard_status}

You can now use this ID in your branch name.
Press Enter or 'g' to generate another.
        """
        )

    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
