"""Task business logic."""

from typing import List, Optional, Dict, Any
from tt.infra.sqlite import Database


class TaskManager:
    """Manages task operations."""

    def __init__(self, db: Optional[Database] = None):
        """Initialize task manager.

        Args:
            db: Database instance. If None, creates a new one.
        """
        self.db = db or Database()

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks.

        Returns:
            List of task dictionaries
        """
        return self.db.get_all_tasks()

    def get_task(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a task by code.

        Args:
            code: Task code (e.g., 'tt-123')

        Returns:
            Task dictionary or None if not found
        """
        return self.db.get_task_by_code(code)

    def link_pr_to_task(
        self,
        task_code: str,
        repo: str,
        pr_number: int,
        title: str,
        body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Link a PR to a task.

        Args:
            task_code: Task code to link to
            repo: Repository name
            pr_number: PR number
            title: PR title
            body: PR body/description

        Returns:
            PR data dictionary
        """
        return self.db.create_pr(task_code, repo, pr_number, title, body)

    def get_prs_for_task(self, task_code: str) -> List[Dict[str, Any]]:
        """Get all PRs linked to a task.

        Args:
            task_code: Task code

        Returns:
            List of PR dictionaries
        """
        return self.db.get_prs_for_task(task_code)

    def delete_task(self, code: str) -> bool:
        """Delete a task.

        Args:
            code: Task code to delete

        Returns:
            True if deleted, False if not found
        """
        return self.db.delete_task(code)
