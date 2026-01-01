"""PR Inbox screen."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, DataTable

from tt.core.tasks import TaskManager
from tt.infra.github import GitHubIntegration


class PRInboxScreen(Screen):
    """Screen for detecting and linking PRs to tasks."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("r", "refresh", "Refresh"),
        ("a", "attach", "Attach PR"),
        ("i", "ignore", "Ignore"),
        ("enter", "attach", "Attach PR"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_manager = TaskManager()
        self.github = GitHubIntegration()
        self.unlinked_prs = []

    def compose(self) -> ComposeResult:
        """Compose the PR inbox screen."""
        yield Header()
        yield Container(
            Static("PR Inbox", classes="screen-title"),
            Static("", id="status-message"),
            Vertical(
                DataTable(id="pr-table"),
                Static(
                    "[dim]Select PR with arrow keys | 'a' or Enter to attach | 'i' to ignore | 'r' to refresh | Escape to go back[/dim]",  # noqa
                    classes="pr-hint",
                ),
                classes="pr-content",
            ),
            classes="screen-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self.scan_for_prs()

    def scan_for_prs(self) -> None:
        """Scan for unlinked PRs."""
        status = self.query_one("#status-message", Static)

        # Check if GitHub CLI is available
        if not self.github.is_gh_available():
            status.update(
                "[red]GitHub CLI (gh) is not available. Please install and authenticate.[/red]"
            )
            self.unlinked_prs = []
            self.update_pr_table()
            return

        status.update("[yellow]Scanning for PRs...[/yellow]")

        # Get all open tasks
        tasks = self.task_manager.get_all_tasks()
        open_tasks = [t for t in tasks if t["status"] == "open"]
        task_codes = [t["code"] for t in open_tasks]

        if not task_codes:
            status.update("[yellow]No open tasks to check.[/yellow]")
            self.unlinked_prs = []
            self.update_pr_table()
            return

        # Find unlinked PRs
        self.unlinked_prs = self.github.find_unlinked_prs(task_codes)

        if not self.unlinked_prs:
            status.update("[green]No unlinked PRs found.[/green]")
        else:
            count = len(self.unlinked_prs)
            status.update(
                f"[green]Found {count} unlinked PR{'s' if count != 1 else ''}[/green]"
            )

        self.update_pr_table()

    def update_pr_table(self) -> None:
        """Update the PR table with unlinked PRs."""
        table = self.query_one("#pr-table", DataTable)
        table.clear(columns=True)

        # Add columns
        table.add_column("Task ID", key="task_id")
        table.add_column("PR #", key="pr_number")
        table.add_column("Branch", key="branch")
        table.add_column("Title", key="title")

        # Add rows
        for pr in self.unlinked_prs:
            table.add_row(
                pr["task_code"],
                f"#{pr['pr_number']}",
                pr["branch"],
                pr["title"][:50] + "..." if len(pr["title"]) > 50 else pr["title"],
                key=str(pr["pr_number"]),
            )

        if not self.unlinked_prs:
            table.add_row("No unlinked PRs", "", "", "")

    def action_attach(self) -> None:
        """Attach the currently highlighted PR to its task."""
        table = self.query_one("#pr-table", DataTable)
        status = self.query_one("#status-message", Static)

        # Get highlighted row
        if table.cursor_row is None or table.cursor_row < 0:
            status.update(
                "[yellow]No PR selected. Use arrow keys to highlight a PR.[/yellow]"
            )
            return

        # Get all row keys
        row_keys = list(table.rows.keys())
        if table.cursor_row >= len(row_keys):
            status.update("[yellow]No PR selected[/yellow]")
            return

        # Get the row key at cursor position
        row_key = row_keys[table.cursor_row]
        pr_number = row_key.value if hasattr(row_key, "value") else str(row_key)

        # Find the PR
        selected_pr = None
        for pr in self.unlinked_prs:
            if str(pr["pr_number"]) == pr_number:
                selected_pr = pr
                break

        if not selected_pr:
            status.update("[yellow]Could not find PR[/yellow]")
            return

        try:
            # Link PR to task
            self.task_manager.link_pr_to_task(
                task_code=selected_pr["task_code"],
                repo=selected_pr["repo"],
                pr_number=selected_pr["pr_number"],
                title=selected_pr["title"],
                body=selected_pr.get("body", ""),
            )

            status.update(
                f"[green]✓ Attached PR #{selected_pr['pr_number']} to {selected_pr['task_code']}[/green]"
            )

            # Refresh the list
            self.scan_for_prs()

        except Exception as e:
            status.update(f"[red]Error: {str(e)}[/red]")

    def action_ignore(self) -> None:
        """Ignore the currently highlighted PR."""
        table = self.query_one("#pr-table", DataTable)
        status = self.query_one("#status-message", Static)

        # Get highlighted row
        if table.cursor_row is None or table.cursor_row < 0:
            status.update("[yellow]No PR selected[/yellow]")
            return

        # Get all row keys
        row_keys = list(table.rows.keys())
        if table.cursor_row >= len(row_keys):
            status.update("[yellow]No PR selected[/yellow]")
            return

        # Get the row key at cursor position
        row_key = row_keys[table.cursor_row]
        pr_number = row_key.value if hasattr(row_key, "value") else str(row_key)

        # Remove from list (just for UI, doesn't persist)
        self.unlinked_prs = [
            pr for pr in self.unlinked_prs if str(pr["pr_number"]) != pr_number
        ]

        self.update_pr_table()
        status.update("[yellow]PR ignored (only for this session)[/yellow]")

    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh the PR list."""
        self.scan_for_prs()
