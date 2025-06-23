"""GitHub API client implementation."""

import os
import subprocess
from datetime import datetime
from typing import Any

import httpx
from pydantic import ValidationError

from ..exceptions import APIError, AuthenticationError, RateLimitError
from .models import GitHubGist, GitHubIssue, GitHubPullRequest, GitHubRepo, GitHubUser, RateLimit


class GitHubClient:
    """GitHub API client with authentication and rate limiting."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://api.github.com",
    ) -> None:
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token. If None, will try to get from
                environment or gh CLI.
            base_url: GitHub API base URL.
        """
        self.base_url = base_url
        self.token = token or self._get_token()
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=30.0,
        )

    def _get_token(self) -> str:
        """Get GitHub token from environment or gh CLI."""
        # Try environment variable first
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        if token:
            return token

        # Try gh CLI
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        raise AuthenticationError(
            "No GitHub token found. Please set GITHUB_TOKEN environment variable "
            "or authenticate with 'gh auth login'"
        )

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "mygh/0.1.0",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to GitHub API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON request body

        Returns:
            Response JSON data

        Raises:
            APIError: For API errors
            RateLimitError: For rate limit exceeded
            AuthenticationError: For authentication errors
        """
        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired GitHub token")
            elif response.status_code == 403:
                if "rate limit exceeded" in response.text.lower():
                    raise RateLimitError("GitHub API rate limit exceeded")
                raise APIError(f"Forbidden: {response.text}", response.status_code)
            elif response.status_code >= 400:
                raise APIError(f"API error: {response.text}", response.status_code)

            return response.json()  # type: ignore[no-any-return]

        except httpx.RequestError as e:
            raise APIError(f"Request failed: {e}") from e

    async def get_user(self, username: str | None = None) -> GitHubUser:
        """Get user information.

        Args:
            username: GitHub username. If None, gets authenticated user.

        Returns:
            User information
        """
        endpoint = f"/users/{username}" if username else "/user"
        data = await self._request("GET", endpoint)

        try:
            return GitHubUser(**data)
        except ValidationError as e:
            raise APIError(f"Invalid user data: {e}") from e

    async def get_starred_repos(
        self,
        username: str | None = None,
        language: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[GitHubRepo]:
        """Get starred repositories.

        Args:
            username: GitHub username. If None, gets authenticated user's
                starred repos.
            language: Filter by programming language
            per_page: Number of results per page (max 100)
            page: Page number

        Returns:
            List of starred repositories
        """
        endpoint = f"/users/{username}/starred" if username else "/user/starred"
        params = {"per_page": min(per_page, 100), "page": page}

        data = await self._request("GET", endpoint, params=params)

        try:
            repos = [GitHubRepo(**repo) for repo in data]  # type: ignore[arg-type]

            # Filter by language if specified
            if language:
                repos = [
                    repo
                    for repo in repos
                    if repo.language and repo.language.lower() == language.lower()
                ]

            return repos
        except ValidationError as e:
            raise APIError(f"Invalid repository data: {e}") from e

    async def get_user_repos(
        self,
        username: str | None = None,
        repo_type: str = "all",
        sort: str = "updated",
        per_page: int = 30,
        page: int = 1,
    ) -> list[GitHubRepo]:
        """Get user repositories.

        Args:
            username: GitHub username. If None, gets authenticated user's repos.
            repo_type: Repository type (all, public, private, owner, member)
            sort: Sort order (created, updated, pushed, full_name)
            per_page: Number of results per page (max 100)
            page: Page number

        Returns:
            List of repositories
        """
        endpoint = f"/users/{username}/repos" if username else "/user/repos"
        params = {
            "type": repo_type,
            "sort": sort,
            "per_page": min(per_page, 100),
            "page": page,
        }

        data = await self._request("GET", endpoint, params=params)

        try:
            return [GitHubRepo(**repo) for repo in data]  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid repository data: {e}") from e

    async def get_user_gists(
        self,
        username: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[GitHubGist]:
        """Get user gists.

        Args:
            username: GitHub username. If None, gets authenticated user's gists.
            per_page: Number of results per page (max 100)
            page: Page number

        Returns:
            List of gists
        """
        endpoint = f"/users/{username}/gists" if username else "/user/gists"
        params = {"per_page": min(per_page, 100), "page": page}

        data = await self._request("GET", endpoint, params=params)

        try:
            return [GitHubGist(**gist) for gist in data]  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid gist data: {e}") from e

    async def get_repo_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        assignee: str | None = None,
        labels: str | None = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[GitHubIssue]:
        """Get repository issues.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            assignee: Filter by assignee
            labels: Filter by labels (comma-separated)
            per_page: Number of results per page (max 100)
            page: Page number

        Returns:
            List of issues
        """
        endpoint = f"/repos/{owner}/{repo}/issues"
        params = {
            "state": state,
            "per_page": min(per_page, 100),
            "page": page,
        }

        if assignee:
            params["assignee"] = assignee
        if labels:
            params["labels"] = labels

        data = await self._request("GET", endpoint, params=params)

        try:
            return [GitHubIssue(**issue) for issue in data]  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid issue data: {e}") from e

    async def get_rate_limit(self) -> RateLimit:
        """Get current rate limit information.

        Returns:
            Rate limit information
        """
        data = await self._request("GET", "/rate_limit")

        try:
            core_limit = data["resources"]["core"]
            return RateLimit(
                limit=core_limit["limit"],
                remaining=core_limit["remaining"],
                reset=datetime.fromtimestamp(core_limit["reset"]),
                used=core_limit["used"],
            )
        except (KeyError, ValidationError) as e:
            raise APIError(f"Invalid rate limit data: {e}") from e

    async def create_repo(self, repo_data: dict) -> GitHubRepo:
        """Create a new repository.

        Args:
            repo_data: Repository creation data

        Returns:
            Created repository
        """
        data = await self._request("POST", "/user/repos", json=repo_data)

        try:
            return GitHubRepo(**data)  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid repository data: {e}") from e

    async def update_repo(self, owner: str, repo: str, update_data: dict) -> GitHubRepo:
        """Update repository settings.

        Args:
            owner: Repository owner
            repo: Repository name
            update_data: Update data

        Returns:
            Updated repository
        """
        endpoint = f"/repos/{owner}/{repo}"
        data = await self._request("PATCH", endpoint, json=update_data)

        try:
            return GitHubRepo(**data)  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid repository data: {e}") from e

    async def delete_repo(self, owner: str, repo: str) -> None:
        """Delete a repository.

        Args:
            owner: Repository owner
            repo: Repository name
        """
        endpoint = f"/repos/{owner}/{repo}"
        await self._request("DELETE", endpoint)

    async def fork_repo(self, owner: str, repo: str, fork_data: dict | None = None) -> GitHubRepo:
        """Fork a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            fork_data: Optional fork data (e.g., organization)

        Returns:
            Forked repository
        """
        endpoint = f"/repos/{owner}/{repo}/forks"
        data = await self._request("POST", endpoint, json=fork_data or {})

        try:
            return GitHubRepo(**data)  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid repository data: {e}") from e

    async def get_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        base: str | None = None,
        head: str | None = None,
        sort: str = "created",
        direction: str = "desc",
        per_page: int = 30,
        page: int = 1,
    ) -> list[GitHubPullRequest]:
        """Get repository pull requests.

        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            base: Filter by base branch
            head: Filter by head branch
            sort: Sort order (created, updated, popularity)
            direction: Sort direction (asc, desc)
            per_page: Number of results per page (max 100)
            page: Page number

        Returns:
            List of pull requests
        """
        endpoint = f"/repos/{owner}/{repo}/pulls"
        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100),
            "page": page,
        }

        if base:
            params["base"] = base
        if head:
            params["head"] = head

        data = await self._request("GET", endpoint, params=params)

        try:
            return [GitHubPullRequest(**pr) for pr in data]  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid pull request data: {e}") from e

    async def get_pull_request(
        self, owner: str, repo: str, pr_number: int
    ) -> GitHubPullRequest:
        """Get a specific pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Pull request details
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        data = await self._request("GET", endpoint)

        try:
            return GitHubPullRequest(**data)  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid pull request data: {e}") from e

    async def create_pull_request(
        self, owner: str, repo: str, pr_data: dict
    ) -> GitHubPullRequest:
        """Create a new pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_data: Pull request creation data

        Returns:
            Created pull request
        """
        endpoint = f"/repos/{owner}/{repo}/pulls"
        data = await self._request("POST", endpoint, json=pr_data)

        try:
            return GitHubPullRequest(**data)  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid pull request data: {e}") from e

    async def update_pull_request(
        self, owner: str, repo: str, pr_number: int, update_data: dict
    ) -> GitHubPullRequest:
        """Update a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            update_data: Update data

        Returns:
            Updated pull request
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        data = await self._request("PATCH", endpoint, json=update_data)

        try:
            return GitHubPullRequest(**data)  # type: ignore[arg-type]
        except ValidationError as e:
            raise APIError(f"Invalid pull request data: {e}") from e

    async def merge_pull_request(
        self, owner: str, repo: str, pr_number: int, merge_data: dict
    ) -> dict:
        """Merge a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number
            merge_data: Merge data

        Returns:
            Merge result
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}/merge"
        return await self._request("PUT", endpoint, json=merge_data)

    async def get_pull_request_diff(
        self, owner: str, repo: str, pr_number: int
    ) -> str:
        """Get pull request diff.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Diff as string
        """
        endpoint = f"/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {"Accept": "application/vnd.github.v3.diff"}
        
        response = await self.client.get(
            f"{self.base_url}{endpoint}",
            headers={**self.headers, **headers}
        )
        
        if response.status_code == 403:
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code == 401:
            raise AuthenticationError("Invalid or missing authentication token")
        elif response.status_code >= 400:
            raise APIError(f"HTTP {response.status_code}: {response.text}")
            
        return response.text

    async def delete_branch(self, owner: str, repo: str, branch: str) -> None:
        """Delete a branch.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
        """
        endpoint = f"/repos/{owner}/{repo}/git/refs/heads/{branch}"
        await self._request("DELETE", endpoint)

    # GitHub Actions methods
    async def get_workflows(self, owner: str, repo: str) -> list[dict]:
        """Get repository workflows."""
        endpoint = f"/repos/{owner}/{repo}/actions/workflows"
        data = await self._request("GET", endpoint)
        return data.get("workflows", [])

    async def get_workflow_runs(
        self, owner: str, repo: str, workflow_id: str | None = None, 
        status: str | None = None, limit: int = 20
    ) -> list[dict]:
        """Get workflow runs."""
        if workflow_id:
            endpoint = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        else:
            endpoint = f"/repos/{owner}/{repo}/actions/runs"
        
        params = {"per_page": limit}
        if status:
            params["status"] = status
            
        data = await self._request("GET", endpoint, params=params)
        return data.get("workflow_runs", [])

    # Organization methods
    async def get_user_organizations(self) -> list[dict]:
        """Get user organizations."""
        data = await self._request("GET", "/user/orgs")
        return data

    async def get_organization_members(self, org: str, role: str | None = None) -> list[dict]:
        """Get organization members."""
        endpoint = f"/orgs/{org}/members"
        params = {}
        if role:
            params["role"] = role
        return await self._request("GET", endpoint, params=params)

    async def get_organization_teams(self, org: str) -> list[dict]:
        """Get organization teams."""
        endpoint = f"/orgs/{org}/teams"
        return await self._request("GET", endpoint)

    async def get_team_members(self, org: str, team_slug: str) -> list[dict]:
        """Get team members."""
        endpoint = f"/orgs/{org}/teams/{team_slug}/members"
        return await self._request("GET", endpoint)

    # Search methods
    async def search_repositories(
        self, query: str, sort: str = "stars", order: str = "desc", limit: int = 20
    ) -> list[dict]:
        """Search repositories."""
        endpoint = "/search/repositories"
        params = {"q": query, "sort": sort, "order": order, "per_page": limit}
        data = await self._request("GET", endpoint, params=params)
        return data.get("items", [])

    async def search_users(
        self, query: str, sort: str = "followers", order: str = "desc", limit: int = 20
    ) -> list[dict]:
        """Search users."""
        endpoint = "/search/users"
        params = {"q": query, "sort": sort, "order": order, "per_page": limit}
        data = await self._request("GET", endpoint, params=params)
        return data.get("items", [])

    # Notification methods
    async def get_notifications(
        self, all_notifications: bool = False, participating: bool = False, limit: int = 20
    ) -> list[dict]:
        """Get notifications."""
        endpoint = "/notifications"
        params = {"per_page": limit}
        if all_notifications:
            params["all"] = "true"
        if participating:
            params["participating"] = "true"
        return await self._request("GET", endpoint, params=params)

    async def mark_notifications_read(self, owner: str, repo: str) -> None:
        """Mark repository notifications as read."""
        endpoint = f"/repos/{owner}/{repo}/notifications"
        await self._request("PUT", endpoint, json={})

    async def mark_all_notifications_read(self) -> None:
        """Mark all notifications as read."""
        endpoint = "/notifications"
        await self._request("PUT", endpoint, json={})

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "GitHubClient":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self, exc_type: type, exc_val: Exception, exc_tb: object
    ) -> None:
        """Async context manager exit."""
        await self.close()
