"""Task ID generation logic."""

from typing import Optional
from tt.infra.sqlite import Database


class IDGenerator:
    """Generates monotonic task IDs."""

    def __init__(self, db: Optional[Database] = None):
        """Initialize ID generator.

        Args:
            db: Database instance. If None, creates a new one.
        """
        self.db = db or Database()

    def generate_next_id(self) -> str:
        """Generate the next task ID.

        Returns:
            Task ID in format 'tt-<number>'
        """
        next_number = self.db.get_next_task_number()
        return f"tt-{next_number}"

    def create_task_with_id(self) -> tuple[str, dict]:
        """Generate a new task ID and create the task.

        Returns:
            Tuple of (task_id, task_data)
        """
        task_id = self.generate_next_id()
        task_data = self.db.create_task(task_id)
        return task_id, task_data
