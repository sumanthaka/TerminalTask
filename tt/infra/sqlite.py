"""SQLite data layer for Task Terminal."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class Database:
    """Handles all SQLite database operations."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Store database in user's home directory
            home = Path.home()
            tt_dir = home / ".tt"
            tt_dir.mkdir(exist_ok=True)
            db_path = str(tt_dir / "tasks.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                created_at DATETIME NOT NULL
            )
        """)

        # Create prs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_code TEXT NOT NULL,
                repo TEXT NOT NULL,
                pr_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (task_code) REFERENCES tasks(code)
            )
        """)

        conn.commit()
        conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_task(self, code: str) -> Dict[str, Any]:
        """Create a new task.

        Args:
            code: Task code (e.g., 'tt-123')

        Returns:
            Dictionary with task data
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        created_at = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO tasks (code, status, created_at)
            VALUES (?, ?, ?)
        """,
            (code, "open", created_at),
        )

        conn.commit()
        task_id = cursor.lastrowid
        conn.close()

        return {"id": task_id, "code": code, "status": "open", "created_at": created_at}

    def get_next_task_number(self) -> int:
        """Get the next task number.

        Returns:
            Next available task number
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(id) as max_id FROM tasks")
        result = cursor.fetchone()
        conn.close()

        max_id = result["max_id"] if result["max_id"] is not None else 0
        return max_id + 1

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks.

        Returns:
            List of task dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.id, t.code, t.status, t.created_at,
                   p.pr_number, p.title, p.body
            FROM tasks t
            LEFT JOIN prs p ON t.code = p.task_code
            ORDER BY t.id DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        tasks = []
        for row in rows:
            tasks.append(
                {
                    "id": row["id"],
                    "code": row["code"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                    "pr_number": row["pr_number"],
                    "pr_title": row["title"],
                    "pr_body": row["body"],
                }
            )

        return tasks

    def get_task_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get a task by its code.

        Args:
            code: Task code (e.g., 'tt-123')

        Returns:
            Task dictionary or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, code, status, created_at
            FROM tasks
            WHERE code = ?
        """,
            (code,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row["id"],
                "code": row["code"],
                "status": row["status"],
                "created_at": row["created_at"],
            }
        return None

    def update_task_status(self, code: str, status: str):
        """Update task status.

        Args:
            code: Task code
            status: New status ('open' or 'linked')
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET status = ?
            WHERE code = ?
        """,
            (status, code),
        )

        conn.commit()
        conn.close()

    def create_pr(
        self,
        task_code: str,
        repo: str,
        pr_number: int,
        title: str,
        body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a PR record and link it to a task.

        Args:
            task_code: Task code to link to
            repo: Repository name (e.g., 'owner/repo')
            pr_number: PR number
            title: PR title
            body: PR body/description

        Returns:
            Dictionary with PR data
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        created_at = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO prs (task_code, repo, pr_number, title, body, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (task_code, repo, pr_number, title, body, created_at),
        )

        pr_id = cursor.lastrowid

        # Update task status to linked
        cursor.execute(
            """
            UPDATE tasks
            SET status = 'linked'
            WHERE code = ?
        """,
            (task_code,),
        )

        conn.commit()
        conn.close()

        return {
            "id": pr_id,
            "task_code": task_code,
            "repo": repo,
            "pr_number": pr_number,
            "title": title,
            "body": body,
            "created_at": created_at,
        }

    def get_prs_for_task(self, task_code: str) -> List[Dict[str, Any]]:
        """Get all PRs linked to a task.

        Args:
            task_code: Task code

        Returns:
            List of PR dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, task_code, repo, pr_number, title, body, created_at
            FROM prs
            WHERE task_code = ?
        """,
            (task_code,),
        )

        rows = cursor.fetchall()
        conn.close()

        prs = []
        for row in rows:
            prs.append(
                {
                    "id": row["id"],
                    "task_code": row["task_code"],
                    "repo": row["repo"],
                    "pr_number": row["pr_number"],
                    "title": row["title"],
                    "body": row["body"],
                    "created_at": row["created_at"],
                }
            )

        return prs

    def delete_task(self, code: str) -> bool:
        """Delete a task and its associated PRs.

        Args:
            code: Task code to delete

        Returns:
            True if task was deleted, False if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Check if task exists
        cursor.execute("SELECT id FROM tasks WHERE code = ?", (code,))
        if cursor.fetchone() is None:
            conn.close()
            return False

        # Delete associated PRs first
        cursor.execute("DELETE FROM prs WHERE task_code = ?", (code,))

        # Delete task
        cursor.execute("DELETE FROM tasks WHERE code = ?", (code,))

        conn.commit()
        conn.close()

        return True
