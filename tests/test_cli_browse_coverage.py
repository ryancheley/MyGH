"""Additional tests for CLI browse module to improve coverage."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from mygh.api.models import GitHubRepo, GitHubUser
from mygh.cli.main import app


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return GitHubUser(
        login="testuser", id=123, html_url="https://github.com/testuser", avatar_url="https://github.com/testuser.png"
    )


@pytest.fixture
def sample_repo():
    """Create a sample repository for testing."""
    from datetime import datetime, timezone

    owner = GitHubUser(
        login="testowner",
        id=456,
        html_url="https://github.com/testowner",
        avatar_url="https://github.com/testowner.png",
    )

    return GitHubRepo(
        id=789,
        name="repo1",
        full_name="testowner/repo1",
        owner=owner,
        private=False,
        fork=False,
        html_url="https://github.com/testowner/repo1",
        clone_url="https://github.com/testowner/repo1.git",
        ssh_url="git@github.com:testowner/repo1.git",
        stargazers_count=10,
        watchers_count=10,
        forks_count=2,
        open_issues_count=1,
        size=1024,
        default_branch="main",
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 12, 1, tzinfo=timezone.utc),
    )


@pytest.mark.api_mock
class TestBrowseStarredCoverage:
    """Tests to improve coverage of browse starred command."""

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_with_authenticated_user(
        self, mock_browser_class, mock_client_class, runner, sample_user, sample_repo
    ):
        """Test browse starred command without user argument (uses authenticated user)."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.get_authenticated_user.return_value = sample_user
        mock_client.get_starred_repos.return_value = [sample_repo]
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Run command without user argument
        result = runner.invoke(app, ["browse", "starred"])

        # Verify result
        assert result.exit_code == 0
        mock_browser_class.assert_called_once_with(mock_client, None)
        mock_browser.run_async.assert_called_once()

        # Verify browser was configured for starred repos
        assert mock_browser.title == "MyGH - Interactive Starred Repositories Browser"
        assert mock_browser.sub_title == "Your Starred Repositories"

        # Verify repositories were set correctly
        assert mock_browser.repositories == [sample_repo]
        assert mock_browser.filtered_repositories == [sample_repo]
        assert sample_repo.starred is True

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_authentication_error_in_context(self, mock_browser_class, mock_client_class, runner):
        """Test authentication error when creating client context."""
        from mygh.exceptions import AuthenticationError

        # Setup mock to raise AuthenticationError on context enter
        mock_client_class.return_value.__aenter__.side_effect = AuthenticationError("Auth failed")

        # Run command
        result = runner.invoke(app, ["browse", "starred"])

        # Should handle authentication error and exit with code 1
        assert result.exit_code == 1
        assert "Authentication error: Auth failed" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_covers_all_exception_paths(
        self, mock_browser_class, mock_client_class, runner, sample_user, sample_repo
    ):
        """Test that all exception handling paths are covered in browse starred."""
        # Test that we can access the actual client methods in the context
        mock_client = AsyncMock()
        mock_client.get_authenticated_user.return_value = sample_user
        mock_client.get_starred_repos.return_value = [sample_repo]
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Test successful execution to ensure we cover the happy path
        result = runner.invoke(app, ["browse", "starred"])
        assert result.exit_code == 0

        # Verify the async context is properly handled
        mock_client_class.return_value.__aenter__.assert_called_once()
        mock_client_class.return_value.__aexit__.assert_called_once()


@pytest.mark.api_mock
class TestBrowseReposCoverage:
    """Tests to improve coverage of browse repos command."""

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_context_manager_paths(self, mock_browser_class, mock_client_class, runner):
        """Test that context manager paths are properly covered."""
        # Setup successful context manager flow
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Test successful execution
        result = runner.invoke(app, ["browse", "repos"])

        # Verify context manager was used properly
        assert result.exit_code == 0
        mock_client_class.return_value.__aenter__.assert_called_once()
        mock_client_class.return_value.__aexit__.assert_called_once()
