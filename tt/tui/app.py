"""Main Textual application."""

from textual.app import App

from tt.tui.screens.menu import MainMenu
from tt.tui.screens.create_task import CreateTaskScreen
from tt.tui.screens.tasks import TasksScreen
from tt.tui.screens.pr_inbox import PRInboxScreen


class TaskTerminalApp(App):
    """Task Terminal TUI application."""

    TITLE = "Task Terminal"
    CSS = """
    /* Main containers */
    .menu-container, .screen-container {
        align: center middle;
        width: 80%;
        height: 100%;
        padding: 2;
    }
    
    /* Title and subtitle */
    .title {
        content-align: center middle;
        text-style: bold;
        color: $primary;
        text-align: center;
        padding: 1;
        width: 100%;
    }
    
    .subtitle {
        content-align: center middle;
        color: $text-muted;
        text-align: center;
        padding: 0 0 2 0;
        width: 100%;
    }
    
    .screen-title {
        content-align: center middle;
        text-style: bold;
        color: $primary;
        text-align: center;
        padding: 1 0 2 0;
        width: 100%;
    }
    
    /* Menu content */
    .menu-content {
        align: center middle;
        width: 50;
        height: auto;
    }
    
    #menu-list {
        width: 100%;
        height: auto;
        min-height: 15;
    }
    
    .menu-hint {
        text-align: center;
        padding: 1;
        color: $text-muted;
    }
    
    /* Create task content */
    .create-task-content {
        align: center middle;
        width: 60;
        height: auto;
    }
    
    .create-task-content #instruction {
        text-align: center;
        padding: 2;
        color: $primary;
    }
    
    .create-task-content #hint {
        text-align: center;
        padding: 1;
        color: $text-muted;
    }
    
    .create-task-content #result {
        text-align: center;
        padding: 2;
        min-height: 8;
    }
    
    /* Tasks content */
    .tasks-content {
        width: 100%;
        height: 100%;
    }
    
    .tasks-content DataTable {
        height: 1fr;
        margin: 1 0;
    }
    
    .tasks-hint {
        text-align: center;
        padding: 1;
        color: $text-muted;
    }
    
    #tasks-status-message {
        text-align: center;
        padding: 1;
        min-height: 3;
    }
    
    /* PR inbox content */
    .pr-content {
        width: 100%;
        height: 100%;
    }
    
    .pr-content DataTable {
        height: 1fr;
        margin: 1 0;
    }
    
    .pr-hint {
        text-align: center;
        padding: 1;
        color: $text-muted;
    }
    
    #status-message {
        text-align: center;
        padding: 1;
        min-height: 3;
    }
    
    /* DataTable styling */
    DataTable {
        background: $surface;
        border: solid $primary;
    }
    
    DataTable > .datatable--header {
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    DataTable > .datatable--cursor {
        background: $secondary;
    }
    """

    SCREENS = {
        "menu": MainMenu,
        "create_task": CreateTaskScreen,
        "tasks": TasksScreen,
        "pr_inbox": PRInboxScreen,
    }

    def on_mount(self) -> None:
        """Initialize the app."""
        self.push_screen("menu")
