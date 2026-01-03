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
        ("l", "link_import", "Link/Import"),
        ("i", "ignore", "Ignore"),
        ("enter", "link_import", "Link/Import"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_manager = TaskManager()
        self.github = GitHubIntegration()
        self.unlinked_prs = []
        self.unimported_ids = []

    def compose(self) -> ComposeResult:
        """Compose the PR inbox screen."""
        yield Header()
        yield Container(
            Static("PR Inbox", classes="screen-title"),
            Static("", id="status-message"),
            Vertical(
                DataTable(id="pr-table"),
                Static(
                    "[dim]'l' or Enter to Link/Import | 'i' to Ignore | 'r' to Refresh | Escape to go back[/dim]",
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
        """Scan for unlinked PRs and unimported task IDs."""
        status = self.query_one("#status-message", Static)

        # Check if GitHub CLI is available
        if not self.github.is_gh_available():
            status.update(
                "[red]GitHub CLI (gh) is not available. Please install and authenticate.[/red]"
            )
            self.unlinked_prs = []
            self.unimported_ids = []
            self.update_pr_table()
            return

        status.update("[yellow]Scanning repository...[/yellow]")

        # Get all existing tasks
        tasks = self.task_manager.get_all_tasks()
        existing_codes = {t["code"] for t in tasks}
        open_task_codes = [t["code"] for t in tasks if t["status"] == "open"]

        # Find unlinked PRs (for existing open tasks)
        self.unlinked_prs = self.github.find_unlinked_prs(open_task_codes)

        # Find all task IDs in repo
        all_ids_in_repo = self.github.find_all_task_ids_in_repo()

        # Find unimported IDs (exist in repo but not locally)
        self.unimported_ids = [
            task_info for task_info in all_ids_in_repo 
            if task_info["task_id"] not in existing_codes
        ]

        total_items = len(self.unlinked_prs) + len(self.unimported_ids)
        if total_items == 0:
            status.update("[green]All synced![/green]")
        else:
            status.update(f"[green]Found {total_items} item(s) to link/import[/green]")

        self.update_pr_table()

    def update_pr_table(self) -> None:
        """Update the PR table with unlinked PRs and unimported task IDs."""
        table = self.query_one("#pr-table", DataTable)
        table.clear(columns=True)

        # Add columns
        table.add_column("Type", key="type")
        table.add_column("Task ID", key="task_id")
        table.add_column("PR #", key="pr_number")
        table.add_column("Branch/Title", key="info")

        # Add unimported task IDs first
        for task_info in self.unimported_ids:
            title = task_info["title"][:50] + "..." if len(task_info["title"]) > 50 else task_info["title"]
            table.add_row(
                "[yellow]Import[/yellow]",
                task_info["task_id"],
                f"#{task_info['pr_number']}",
                title,
                key=f"import_{task_info['task_id']}",
            )

        # Add unlinked PRs
        for pr in self.unlinked_prs:
            table.add_row(
                "[green]Link[/green]",
                pr["task_code"],
                f"#{pr['pr_number']}",
                pr["title"][:50] + "..." if len(pr["title"]) > 50 else pr["title"],
                key=f"pr_{pr['pr_number']}",
            )

        if not self.unimported_ids and not self.unlinked_prs:
            table.add_row("[dim]All synced[/dim]", "", "", "")

    def action_link_import(self) -> None:
        """Link PR or import task ID based on selection."""
        table = self.query_one("#pr-table", DataTable)
        status = self.query_one("#status-message", Static)

        if table.cursor_row is None or table.cursor_row < 0:
            status.update("[yellow]No item selected[/yellow]")
            return

        row_keys = list(table.rows.keys())
        if table.cursor_row >= len(row_keys):
            status.update("[yellow]No item selected[/yellow]")
            return

        row_key = row_keys[table.cursor_row]
        key_str = row_key.value if hasattr(row_key, "value") else str(row_key)

        # Check if it's an import or link action
        if key_str.startswith("import_"):
            task_id = key_str.replace("import_", "")
            
            # Find the task info
            task_info = None
            for info in self.unimported_ids:
                if info["task_id"] == task_id:
                    task_info = info
                    break
            
            if not task_info:
                status.update("[red]Task info not found[/red]")
                return
            
            try:
                # Create the task locally
                self.task_manager.db.create_task(task_id)
                
                # Also link the PR if available
                if task_info["pr_number"]:
                    self.task_manager.link_pr_to_task(
                        task_code=task_id,
                        repo=task_info["repo"],
                        pr_number=task_info["pr_number"],
                        title=task_info["title"],
                        body=task_info.get("body", ""),
                    )
                    status.update(f"[green]✓ Imported {task_id} and linked PR #{task_info['pr_number']}[/green]")
                else:
                    status.update(f"[green]✓ Imported {task_id}[/green]")
                
                self.scan_for_prs()
            except Exception as e:
                status.update(f"[red]Error importing: {str(e)}[/red]")

        elif key_str.startswith("pr_"):
            # This is a PR link action
            pr_number = key_str.replace("pr_", "")
            
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
        """Ignore the currently highlighted item."""
        table = self.query_one("#pr-table", DataTable)
        status = self.query_one("#status-message", Static)

        if table.cursor_row is None or table.cursor_row < 0:
            status.update("[yellow]No item selected[/yellow]")
            return

        row_keys = list(table.rows.keys())
        if table.cursor_row >= len(row_keys):
            status.update("[yellow]No item selected[/yellow]")
            return

        row_key = row_keys[table.cursor_row]
        key_str = row_key.value if hasattr(row_key, "value") else str(row_key)

        # Remove from appropriate list
        if key_str.startswith("import_"):
            task_id = key_str.replace("import_", "")
            self.unimported_ids = [
                info for info in self.unimported_ids if info["task_id"] != task_id
            ]
            status.update(f"[yellow]Ignored {task_id} (session only)[/yellow]")
        elif key_str.startswith("pr_"):
            pr_number = key_str.replace("pr_", "")
            self.unlinked_prs = [
                pr for pr in self.unlinked_prs if str(pr["pr_number"]) != pr_number
            ]
            status.update("[yellow]Ignored PR (session only)[/yellow]")

        self.update_pr_table()

    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()

    def action_refresh(self) -> None:
        """Refresh the PR list."""
        self.scan_for_prs()
