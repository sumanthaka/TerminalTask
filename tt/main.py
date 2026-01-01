"""Task Terminal entry point."""

from tt.tui.app import TaskTerminalApp


def main():
    """Run the Task Terminal application."""
    app = TaskTerminalApp()
    app.run()


if __name__ == "__main__":
    main()
