"""GitHub integration for PR detection and linking."""

import json
import re
import subprocess
from typing import List, Dict, Any, Optional


class GitHubIntegration:
    """Handles GitHub PR detection and linking."""

    def __init__(self):
        """Initialize GitHub integration."""
        pass

    def _run_gh_command(self, args: List[str]) -> Optional[str]:
        """Run a GitHub CLI command.

        Args:
            args: Command arguments for gh CLI

        Returns:
            Command output or None if command failed
        """
        try:
            result = subprocess.run(
                ["gh"] + args, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def is_gh_available(self) -> bool:
        """Check if GitHub CLI is available.

        Returns:
            True if gh CLI is installed and authenticated
        """
        output = self._run_gh_command(["auth", "status"])
        return output is not None

    def get_current_repo(self) -> Optional[str]:
        """Get the current repository name.

        Returns:
            Repository name in format 'owner/repo' or None
        """
        output = self._run_gh_command(
            ["repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]
        )
        return output

    def find_prs_with_task_id(
        self, task_id: str, repo: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find PRs that reference a task ID.

        Args:
            task_id: Task ID to search for (e.g., 'tt-123')
            repo: Repository to search in. If None, uses current repo.

        Returns:
            List of PR dictionaries with keys: number, title, body, branch
        """
        if repo is None:
            repo = self.get_current_repo()
            if repo is None:
                return []

        # Search for PRs with task ID in title or branch
        # Using gh pr list with JSON output
        output = self._run_gh_command(
            [
                "pr",
                "list",
                "--repo",
                repo,
                "--json",
                "number,title,body,headRefName",
                "--limit",
                "100",
            ]
        )

        if output is None:
            return []

        try:
            prs = json.loads(output)
        except json.JSONDecodeError:
            return []

        # Filter PRs that contain the task ID
        matching_prs = []
        task_pattern = re.compile(re.escape(task_id), re.IGNORECASE)

        for pr in prs:
            # Check if task ID is in branch name or title
            branch = pr.get("headRefName", "")
            title = pr.get("title", "")

            if task_pattern.search(branch) or task_pattern.search(title):
                matching_prs.append(
                    {
                        "number": pr.get("number"),
                        "title": title,
                        "body": pr.get("body", ""),
                        "branch": branch,
                    }
                )

        return matching_prs

    def get_pr_details(
        self, pr_number: int, repo: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get details for a specific PR.

        Args:
            pr_number: PR number
            repo: Repository name. If None, uses current repo.

        Returns:
            PR dictionary or None if not found
        """
        if repo is None:
            repo = self.get_current_repo()
            if repo is None:
                return None

        output = self._run_gh_command(
            [
                "pr",
                "view",
                str(pr_number),
                "--repo",
                repo,
                "--json",
                "number,title,body,headRefName",
            ]
        )

        if output is None:
            return None

        try:
            pr = json.loads(output)
            return {
                "number": pr.get("number"),
                "title": pr.get("title", ""),
                "body": pr.get("body", ""),
                "branch": pr.get("headRefName", ""),
            }
        except json.JSONDecodeError:
            return None

    def find_unlinked_prs(self, existing_task_codes: List[str]) -> List[Dict[str, Any]]:
        """Find PRs that contain task IDs but aren't yet linked.

        Args:
            existing_task_codes: List of task codes to search for

        Returns:
            List of dictionaries with keys: task_code, pr_number, title, body, branch
        """
        repo = self.get_current_repo()
        if repo is None:
            return []

        unlinked = []

        for task_code in existing_task_codes:
            prs = self.find_prs_with_task_id(task_code, repo)
            for pr in prs:
                unlinked.append(
                    {
                        "task_code": task_code,
                        "pr_number": pr["number"],
                        "title": pr["title"],
                        "body": pr["body"],
                        "branch": pr["branch"],
                        "repo": repo,
                    }
                )

        return unlinked

    def find_all_task_ids_in_repo(self) -> List[Dict[str, Any]]:
        """Scan all branches and PRs for task IDs.

        Returns:
            List of dicts with keys: task_id, pr_number, title, body, branch, repo
        """
        repo = self.get_current_repo()
        if repo is None:
            return []

        found_tasks = {}
        task_pattern = re.compile(r'\btt-(\d+)\b', re.IGNORECASE)

        # Scan PR titles and branches
        output = self._run_gh_command(
            [
                "pr",
                "list",
                "--repo",
                repo,
                "--json",
                "number,title,body,headRefName",
                "--limit",
                "100",
                "--state",
                "all",
            ]
        )

        if output:
            try:
                prs = json.loads(output)
                for pr in prs:
                    branch = pr.get("headRefName", "")
                    title = pr.get("title", "")
                    
                    # Check branch name
                    matches = task_pattern.findall(branch)
                    for match in matches:
                        task_id = f"tt-{match}"
                        if task_id not in found_tasks:
                            found_tasks[task_id] = {
                                "task_id": task_id,
                                "pr_number": pr.get("number"),
                                "title": title,
                                "body": pr.get("body", ""),
                                "branch": branch,
                                "repo": repo,
                            }

                    # Check title
                    matches = task_pattern.findall(title)
                    for match in matches:
                        task_id = f"tt-{match}"
                        if task_id not in found_tasks:
                            found_tasks[task_id] = {
                                "task_id": task_id,
                                "pr_number": pr.get("number"),
                                "title": title,
                                "body": pr.get("body", ""),
                                "branch": branch,
                                "repo": repo,
                            }
            except json.JSONDecodeError:
                pass

        # Sort by task ID number
        return sorted(
            list(found_tasks.values()),
            key=lambda x: int(x["task_id"].split('-')[1])
        )
