"""Tasks screen."""

import subprocess
import webbrowser
from datetime import datetime
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, DataTable

from tt.core.tasks import TaskManager


class TasksScreen(Screen):
    """Screen for displaying all tasks."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("r", "refresh", "Refresh"),
        ("d", "delete", "Delete"),
        ("o", "open_pr", "Open PR"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_manager = TaskManager()
        self.selected_task_code = None

    def compose(self) -> ComposeResult:
        """Compose the tasks screen."""
        yield Header()
        yield Container(
            Static("Tasks", classes="screen-title"),
            Static("", id="tasks-status-message"),
            Vertical(
                DataTable(id="tasks-table"),
                Static(
                    "[dim]Select a task | 'd' to delete | 'o' to open PR | 'r' to refresh | Escape to go back[/dim]",
                    classes="tasks-hint",
                ),
                classes="tasks-content",
            ),
            classes="screen-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the screen when mounted."""
        self.load_tasks()

    def load_tasks(self) -> None:
        """Load and display tasks."""
        table = self.query_one("#tasks-table", DataTable)
        table.clear(columns=True)

        # Add columns
        table.add_column("ID", key="id")
        table.add_column("Status", key="status")
        table.add_column("Created", key="created")
        table.add_column("PR", key="pr")
        table.add_column("Title", key="title")

        # Get tasks
        tasks = self.task_manager.get_all_tasks()

        # Add rows
        for task in tasks:
            # Format created date
            try:
                created_dt = datetime.fromisoformat(task["created_at"])
                created_str = created_dt.strftime("%Y-%m-%d %I:%M%p")
            except Exception:
                created_str = task["created_at"]

            # Format PR number
            pr_str = f"#{task['pr_number']}" if task["pr_number"] else "-"

            # Format PR title (truncate if too long)
            pr_title = task.get("pr_title") or ""
            if pr_title:
                title_str = pr_title[:60] + "..." if len(pr_title) > 60 else pr_title
            else:
                title_str = "-"

            # Format status with color
            status = task["status"]
            if status == "linked":
                status_str = f"[green]{status}[/green]"
            else:
                status_str = f"[yellow]{status}[/yel, low]"

            table.add_row(
                task["code"],
                status_str,
                created_str,
                pr_str,
                title_str,
                key=task["code"],
            )

        if not tasks:
            table.add_row("No tasks yet", "", "", "")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection."""
        if event.row_key and event.row_key.value:
            # Find the task code for this row
            tasks = self.task_manager.get_all_tasks()
            for task in tasks:
                if str(task["id"]) == event.row_key.value:
                    self.selected_task_code = task["code"]
                    break

    def action_delete(self) -> None:
        """Delete the currently highlighted task."""
        table = self.query_one("#tasks-table", DataTable)
        status = self.query_one("#tasks-status-message", Static)

        # Get the currently highlighted row
        if table.cursor_row is None or table.cursor_row < 0:
            status.update(
                "[yellow]No task selected. Use arrow keys to highlight a task.[/yellow]"
            )
            return

        # Get all row keys
        row_keys = list(table.rows.keys())
        if table.cursor_row >= len(row_keys):
            status.update("[yellow]No task selected[/yellow]")
            return

        # Get the row key at cursor position (this is the task code)
        row_key = row_keys[table.cursor_row]
        task_code = row_key.value if hasattr(row_key, "value") else str(row_key)

        if not task_code or task_code == "No tasks yet":
            status.update("[yellow]No task to delete[/yellow]")
            return

        # Delete the task
        success = self.task_manager.delete_task(task_code)

        if success:
            status.update(f"[green]✓ Deleted {task_code}[/green]")
            self.load_tasks()
        else:
            status.update(f"[red]Failed to delete {task_code}[/red]")

    def action_open_pr(self) -> None:
        """Open the PR in browser for the highlighted task."""
        table = self.query_one("#tasks-table", DataTable)
        status = self.query_one("#tasks-status-message", Static)

        # Get highlighted row
        if table.cursor_row is None or table.cursor_row < 0:
            status.update(
                "[yellow]No task selected. Use arrow keys to highlight a task.[/yellow]"
            )
            return

        # Get all row keys
        row_keys = list(table.rows.keys())
        if table.cursor_row >= len(row_keys):
            status.update("[yellow]No task selected[/yellow]")
            return

        # Get the row key at cursor position (this is the task code)
        row_key = row_keys[table.cursor_row]
        task_code = row_key.value if hasattr(row_key, "value") else str(row_key)

        if not task_code or task_code == "No tasks yet":
            status.update("[yellow]No task to open[/yellow]")
            return

        # Get PRs for this task
        prs = self.task_manager.get_prs_for_task(task_code)

        if not prs:
            status.update(f"[yellow]No PR linked to {task_code}[/yellow]")
            return

        # Get the first PR (assuming one PR per task)
        pr = prs[0]
        pr_number = pr["pr_number"]
        repo = pr["repo"]

        # Try to open with gh CLI first, fallback to browser
        try:
            result = subprocess.run(
                ["gh", "pr", "view", str(pr_number), "--repo", repo, "--web"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                status.update(f"[green]✓ Opened PR #{pr_number} in browser[/green]")
            else:
                # Fallback to direct URL
                pr_url = f"https://github.com/{repo}/pull/{pr_number}"
                webbrowser.open(pr_url)
                status.update(f"[green]✓ Opened PR #{pr_number} in browser[/green]")
        except FileNotFoundError:
            # gh not available, use direct URL
            pr_url = f"https://github.com/{repo}/pull/{pr_number}"
            webbrowser.open(pr_url)
            status.update(f"[green]✓ Opened PR #{pr_number} in browser[/green]")
        except Exception as e:
            status.update(f"[red]Error opening PR: {str(e)}[/red]")

    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh the tasks list."""
        status = self.query_one("#tasks-status-message", Static)
        status.update("")
        self.load_tasks()
