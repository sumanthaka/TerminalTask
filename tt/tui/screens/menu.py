"""Main Menu screen."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, OptionList
from textual.widgets.option_list import Option


class MainMenu(Screen):
    """Main menu screen with navigation options."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("enter", "select", "Select"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the main menu."""
        yield Header()
        yield Container(
            Static("Task Terminal", classes="title"),
            Static("A local-first developer tool for task IDs", classes="subtitle"),
            Vertical(
                OptionList(
                    Option("Create Task", id="create_task"),
                    Option("Tasks", id="tasks"),
                    Option("PR Inbox", id="pr_inbox"),
                    Option("Settings (Coming Soon)", id="settings", disabled=True),
                    Option("Quit", id="quit"),
                    id="menu-list",
                ),
                Static(
                    "[dim]Use arrow keys to navigate, Enter to select[/dim]",
                    classes="menu-hint",
                ),
                classes="menu-content",
            ),
            classes="menu-container",
        )
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle menu selection."""
        option_id = event.option_id

        if option_id == "create_task":
            self.app.push_screen("create_task")
        elif option_id == "tasks":
            self.app.push_screen("tasks")
        elif option_id == "pr_inbox":
            self.app.push_screen("pr_inbox")
        elif option_id == "quit":
            self.app.exit()

    def action_select(self) -> None:
        """Handle Enter key to select current option."""
        option_list = self.query_one("#menu-list", OptionList)
        if option_list.highlighted is not None:
            option_list.action_select()

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
