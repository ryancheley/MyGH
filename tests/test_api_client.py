"""Tests for GitHub API client."""

import subprocess
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
import respx

from mygh.api.client import GitHubClient
from mygh.api.models import GitHubGist, GitHubIssue, GitHubRepo, GitHubUser, RateLimit
from mygh.exceptions import APIError, AuthenticationError, RateLimitError


class TestGitHubClient:
    """Test GitHub API client."""

    def test_init_with_token(self):
        """Test client initialization with token."""
        client = GitHubClient(token="test_token")
        assert client.token == "test_token"
        assert client.base_url == "https://api.github.com"
        assert "Authorization" in client._get_headers()
        assert client._get_headers()["Authorization"] == "token test_token"

    def test_init_without_token_with_env_var(self, mock_github_token):
        """Test client initialization without token but with env var."""
        client = GitHubClient()
        assert client.token == "test_token_123"

    @patch.dict("os.environ", {}, clear=True)
    @patch("subprocess.run")
    def test_init_with_gh_cli(self, mock_subprocess):
        """Test client initialization using gh CLI."""
        mock_subprocess.return_value = Mock(
            stdout="gh_cli_token\n",
            returncode=0,
        )

        client = GitHubClient()
        assert client.token == "gh_cli_token"
        mock_subprocess.assert_called_once_with(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch.dict("os.environ", {}, clear=True)
    @patch("subprocess.run")
    def test_init_no_token_available(self, mock_subprocess):
        """Test client initialization when no token is available."""
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "gh")

        with pytest.raises(AuthenticationError, match="No GitHub token found"):
            GitHubClient()

    def test_get_headers(self):
        """Test HTTP headers generation."""
        client = GitHubClient(token="test_token")
        headers = client._get_headers()

        assert headers["Accept"] == "application/vnd.github.v3+json"
        assert headers["User-Agent"] == "mygh/0.1.0"
        assert headers["Authorization"] == "token test_token"

    def test_get_headers_no_token(self):
        """Test HTTP headers without token."""
        with patch.object(GitHubClient, "_get_token", return_value=""):
            client = GitHubClient()
            client.token = ""
            headers = client._get_headers()
            assert "Authorization" not in headers

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_github_token):
        """Test async context manager functionality."""
        async with GitHubClient() as client:
            assert isinstance(client, GitHubClient)
            assert client.token == "test_token_123"
        # Client should be closed after context exit

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_success(self, mock_github_token):
        """Test successful API request."""
        respx.get("https://api.github.com/test").mock(
            return_value=httpx.Response(200, json={"message": "success"})
        )

        client = GitHubClient()
        result = await client._request("GET", "/test")
        assert result == {"message": "success"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_401_error(self, mock_github_token):
        """Test 401 authentication error."""
        respx.get("https://api.github.com/test").mock(
            return_value=httpx.Response(401, text="Unauthorized")
        )

        client = GitHubClient()
        with pytest.raises(
            AuthenticationError, match="Invalid or expired GitHub token"
        ):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_403_rate_limit(self, mock_github_token):
        """Test 403 rate limit error."""
        respx.get("https://api.github.com/test").mock(
            return_value=httpx.Response(403, text="rate limit exceeded")
        )

        client = GitHubClient()
        with pytest.raises(RateLimitError, match="GitHub API rate limit exceeded"):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_403_forbidden(self, mock_github_token):
        """Test 403 forbidden error."""
        respx.get("https://api.github.com/test").mock(
            return_value=httpx.Response(403, text="Forbidden")
        )

        client = GitHubClient()
        with pytest.raises(APIError, match="Forbidden"):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_400_error(self, mock_github_token):
        """Test 400+ error."""
        respx.get("https://api.github.com/test").mock(
            return_value=httpx.Response(404, text="Not Found")
        )

        client = GitHubClient()
        with pytest.raises(APIError, match="API error: Not Found"):
            await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_request_network_error(self, mock_github_token):
        """Test network error handling."""
        client = GitHubClient()

        with patch.object(
            client.client, "request", side_effect=httpx.RequestError("Network error")
        ):
            with pytest.raises(APIError, match="Request failed: Network error"):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_authenticated(self, mock_github_token, sample_user_data):
        """Test getting authenticated user."""
        respx.get("https://api.github.com/user").mock(
            return_value=httpx.Response(200, json=sample_user_data)
        )

        client = GitHubClient()
        user = await client.get_user()

        assert isinstance(user, GitHubUser)
        assert user.login == "testuser"
        assert user.name == "Test User"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_by_username(self, mock_github_token, sample_user_data):
        """Test getting user by username."""
        respx.get("https://api.github.com/users/testuser").mock(
            return_value=httpx.Response(200, json=sample_user_data)
        )

        client = GitHubClient()
        user = await client.get_user("testuser")

        assert isinstance(user, GitHubUser)
        assert user.login == "testuser"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_invalid_data(self, mock_github_token):
        """Test getting user with invalid data."""
        respx.get("https://api.github.com/user").mock(
            return_value=httpx.Response(200, json={"invalid": "data"})
        )

        client = GitHubClient()
        with pytest.raises(APIError, match="Invalid user data"):
            await client.get_user()

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_starred_repos(self, mock_github_token, sample_repo_data):
        """Test getting starred repositories."""
        repos_data = [sample_repo_data]
        respx.get("https://api.github.com/user/starred").mock(
            return_value=httpx.Response(200, json=repos_data)
        )

        client = GitHubClient()
        repos = await client.get_starred_repos()

        assert len(repos) == 1
        assert isinstance(repos[0], GitHubRepo)
        assert repos[0].name == "test-repo"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_starred_repos_with_language_filter(
        self, mock_github_token, sample_repo_data
    ):
        """Test getting starred repositories with language filter."""
        repos_data = [sample_repo_data]
        respx.get("https://api.github.com/user/starred").mock(
            return_value=httpx.Response(200, json=repos_data)
        )

        client = GitHubClient()
        repos = await client.get_starred_repos(language="Python")

        assert len(repos) == 1
        assert repos[0].language == "Python"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_starred_repos_language_filter_no_match(
        self, mock_github_token, sample_repo_data
    ):
        """Test language filter with no matches."""
        repos_data = [sample_repo_data]
        respx.get("https://api.github.com/user/starred").mock(
            return_value=httpx.Response(200, json=repos_data)
        )

        client = GitHubClient()
        repos = await client.get_starred_repos(language="Go")

        assert len(repos) == 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_repos(self, mock_github_token, sample_repo_data):
        """Test getting user repositories."""
        repos_data = [sample_repo_data]
        respx.get("https://api.github.com/user/repos").mock(
            return_value=httpx.Response(200, json=repos_data)
        )

        client = GitHubClient()
        repos = await client.get_user_repos()

        assert len(repos) == 1
        assert isinstance(repos[0], GitHubRepo)

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_repos_with_params(
        self, mock_github_token, sample_repo_data
    ):
        """Test getting user repositories with parameters."""
        repos_data = [sample_repo_data]
        respx.get("https://api.github.com/users/testuser/repos").mock(
            return_value=httpx.Response(200, json=repos_data)
        )

        client = GitHubClient()
        repos = await client.get_user_repos(
            username="testuser", repo_type="public", sort="created", per_page=50, page=2
        )

        assert len(repos) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_user_gists(self, mock_github_token, sample_gist_data):
        """Test getting user gists."""
        gists_data = [sample_gist_data]
        respx.get("https://api.github.com/user/gists").mock(
            return_value=httpx.Response(200, json=gists_data)
        )

        client = GitHubClient()
        gists = await client.get_user_gists()

        assert len(gists) == 1
        assert isinstance(gists[0], GitHubGist)
        assert gists[0].id == "abc123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_repo_issues(self, mock_github_token, sample_issue_data):
        """Test getting repository issues."""
        issues_data = [sample_issue_data]
        respx.get("https://api.github.com/repos/testuser/test-repo/issues").mock(
            return_value=httpx.Response(200, json=issues_data)
        )

        client = GitHubClient()
        issues = await client.get_repo_issues("testuser", "test-repo")

        assert len(issues) == 1
        assert isinstance(issues[0], GitHubIssue)
        assert issues[0].title == "Test issue"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_repo_issues_with_filters(
        self, mock_github_token, sample_issue_data
    ):
        """Test getting repository issues with filters."""
        issues_data = [sample_issue_data]
        respx.get("https://api.github.com/repos/testuser/test-repo/issues").mock(
            return_value=httpx.Response(200, json=issues_data)
        )

        client = GitHubClient()
        issues = await client.get_repo_issues(
            "testuser",
            "test-repo",
            state="closed",
            assignee="testuser",
            labels="bug,help wanted",
        )

        assert len(issues) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_rate_limit(self, mock_github_token):
        """Test getting rate limit information."""
        rate_limit_data = {
            "resources": {
                "core": {
                    "limit": 5000,
                    "remaining": 4999,
                    "reset": 1640995200,
                    "used": 1,
                }
            }
        }
        respx.get("https://api.github.com/rate_limit").mock(
            return_value=httpx.Response(200, json=rate_limit_data)
        )

        client = GitHubClient()
        rate_limit = await client.get_rate_limit()

        assert isinstance(rate_limit, RateLimit)
        assert rate_limit.limit == 5000
        assert rate_limit.remaining == 4999
        assert rate_limit.used == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_rate_limit_invalid_data(self, mock_github_token):
        """Test getting rate limit with invalid data."""
        respx.get("https://api.github.com/rate_limit").mock(
            return_value=httpx.Response(200, json={"invalid": "data"})
        )

        client = GitHubClient()
        with pytest.raises(APIError, match="Invalid rate limit data"):
            await client.get_rate_limit()

    @pytest.mark.asyncio
    async def test_close(self, mock_github_token):
        """Test client close method."""
        client = GitHubClient()

        with patch.object(
            client.client, "aclose", new_callable=AsyncMock
        ) as mock_close:
            await client.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    @respx.mock
    async def test_pagination_params(self, mock_github_token, sample_repo_data):
        """Test that pagination parameters are properly applied."""
        repos_data = [sample_repo_data]

        # Mock the request with specific query parameters
        request_mock = respx.get(
            "https://api.github.com/user/starred", params={"per_page": 100, "page": 2}
        ).mock(return_value=httpx.Response(200, json=repos_data))

        client = GitHubClient()
        await client.get_starred_repos(per_page=100, page=2)

        assert request_mock.called

    @pytest.mark.asyncio
    @respx.mock
    async def test_per_page_limit_enforcement(
        self, mock_github_token, sample_repo_data
    ):
        """Test that per_page parameter is limited to 100."""
        repos_data = [sample_repo_data]

        # Should limit to 100 even if we request 150
        request_mock = respx.get(
            "https://api.github.com/user/starred", params={"per_page": 100, "page": 1}
        ).mock(return_value=httpx.Response(200, json=repos_data))

        client = GitHubClient()
        await client.get_starred_repos(per_page=150)

        assert request_mock.called
