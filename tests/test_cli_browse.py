"""Tests for the browse CLI commands."""

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
def mock_github_client():
    """Create a mock GitHub client."""
    return AsyncMock()


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return GitHubUser(
        login="testuser", id=123, html_url="https://github.com/testuser", avatar_url="https://github.com/testuser.png"
    )


@pytest.fixture
def sample_repos():
    """Create sample repositories for testing."""
    from datetime import datetime, timezone

    owner = GitHubUser(
        login="testowner",
        id=456,
        html_url="https://github.com/testowner",
        avatar_url="https://github.com/testowner.png",
    )

    repo1 = GitHubRepo(
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

    repo2 = GitHubRepo(
        id=790,
        name="repo2",
        full_name="testowner/repo2",
        owner=owner,
        private=True,
        fork=False,
        html_url="https://github.com/testowner/repo2",
        clone_url="https://github.com/testowner/repo2.git",
        ssh_url="git@github.com:testowner/repo2.git",
        stargazers_count=5,
        watchers_count=5,
        forks_count=1,
        open_issues_count=0,
        size=512,
        default_branch="main",
        created_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 12, 15, tzinfo=timezone.utc),
    )

    return [repo1, repo2]


class TestBrowseCommands:
    """Test the browse CLI commands."""

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_command(self, mock_browser_class, mock_client_class, runner):
        """Test the browse repos command."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "repos"])

        # Verify result
        assert result.exit_code == 0
        mock_browser_class.assert_called_once_with(mock_client, None)
        mock_browser.run_async.assert_called_once()

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_with_user(self, mock_browser_class, mock_client_class, runner):
        """Test the browse repos command with specific user."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Run command with user option
        result = runner.invoke(app, ["browse", "repos", "--user", "testuser"])

        # Verify result
        assert result.exit_code == 0
        mock_browser_class.assert_called_once_with(mock_client, "testuser")
        mock_browser.run_async.assert_called_once()

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_keyboard_interrupt(self, mock_browser_class, mock_client_class, runner):
        """Test handling keyboard interrupt in browse repos."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=KeyboardInterrupt)
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "repos"])

        # Should handle KeyboardInterrupt gracefully
        assert result.exit_code == 0
        assert "Browser closed" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_error(self, mock_browser_class, mock_client_class, runner):
        """Test handling errors in browse repos."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=Exception("Test error"))
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "repos"])

        # Should handle error and exit with code 1
        assert result.exit_code == 1
        assert "Error running browser: Test error" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_command(self, mock_browser_class, mock_client_class, runner):
        """Test the browse starred command."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "starred"])

        # Verify result
        assert result.exit_code == 0
        mock_browser_class.assert_called_once_with(mock_client, None)
        mock_browser.run_async.assert_called_once()

        # Verify browser was configured for starred repos
        assert mock_browser.title == "MyGH - Interactive Starred Repositories Browser"
        assert mock_browser.sub_title == "Your Starred Repositories"

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_with_user(self, mock_browser_class, mock_client_class, runner):
        """Test the browse starred command with specific user."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Run command with user option
        result = runner.invoke(app, ["browse", "starred", "--user", "testuser"])

        # Verify result
        assert result.exit_code == 0
        mock_browser_class.assert_called_once_with(mock_client, "testuser")

        # Verify browser was configured for starred repos with user
        assert mock_browser.title == "MyGH - Interactive Starred Repositories Browser"
        assert mock_browser.sub_title == "Starred by: testuser"


class TestBrowseCommandHelp:
    """Test help output for browse commands."""

    def test_browse_help(self, runner):
        """Test browse command help."""
        result = runner.invoke(app, ["browse", "--help"])
        assert result.exit_code == 0
        assert "Interactive repository browser" in result.stdout

    def test_browse_repos_help(self, runner):
        """Test browse repos command help."""
        result = runner.invoke(app, ["browse", "repos", "--help"])
        assert result.exit_code == 0
        assert "Launch interactive repository browser" in result.stdout
        # Check for --user option in different formats (with or without ANSI codes)
        assert ("--user" in result.stdout or "-u" in result.stdout)

    def test_browse_starred_help(self, runner):
        """Test browse starred command help."""
        result = runner.invoke(app, ["browse", "starred", "--help"])
        assert result.exit_code == 0
        assert "Launch interactive browser for starred repositories" in result.stdout
        # Check for --user option in different formats (with or without ANSI codes)
        assert ("--user" in result.stdout or "-u" in result.stdout)


@pytest.mark.api_mock
class TestBrowseIntegration:
    """Integration tests for browse commands."""

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_full_browse_workflow(self, mock_browser_class, mock_client_class, runner, sample_repos, sample_user):
        """Test a complete browse workflow."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client.get_authenticated_user.return_value = sample_user
        mock_client.get_user_repos.return_value = sample_repos
        mock_client.get_starred_repos.return_value = [sample_repos[0]]

        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock()
        mock_browser_class.return_value = mock_browser

        # Run browse repos command
        result = runner.invoke(app, ["browse", "repos", "--user", "testuser"])

        # Verify successful execution
        assert result.exit_code == 0
        mock_browser_class.assert_called_once_with(mock_client, "testuser")
        mock_browser.run_async.assert_called_once()

    def test_browse_command_in_main_app(self, runner):
        """Test that browse command is properly registered in main app."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "browse" in result.stdout
        assert "Interactive repository browser" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_authentication_error(self, mock_browser_class, mock_client_class, runner):
        """Test handling authentication error in browse starred."""
        # Setup mocks to raise AuthenticationError
        mock_client_class.return_value.__aenter__.side_effect = Exception("Auth test")

        # Run command
        result = runner.invoke(app, ["browse", "starred"])

        # Should handle error and exit with code 1
        assert result.exit_code == 1
        assert "Error running starred browser: Auth test" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_authentication_handling(self, mock_browser_class, mock_client_class, runner):
        """Test authentication error handling in browse repos."""
        from mygh.exceptions import AuthenticationError

        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=AuthenticationError("Token invalid"))
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "repos"])

        # Should handle authentication error properly
        assert result.exit_code == 1
        assert "Authentication error: Token invalid" in result.stdout
        assert "To authenticate:" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_api_error(self, mock_browser_class, mock_client_class, runner):
        """Test API error handling in browse repos."""
        from mygh.exceptions import APIError

        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=APIError("Rate limit exceeded"))
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "repos"])

        # Should handle API error properly
        assert result.exit_code == 1
        assert "API error: Rate limit exceeded" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_repos_mygh_exception(self, mock_browser_class, mock_client_class, runner):
        """Test MyGH exception handling in browse repos."""
        from mygh.exceptions import MyGHException

        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=MyGHException("Custom error"))
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "repos"])

        # Should handle MyGH exception properly
        assert result.exit_code == 1
        assert "Error: Custom error" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_keyboard_interrupt(self, mock_browser_class, mock_client_class, runner):
        """Test handling keyboard interrupt in browse starred."""
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=KeyboardInterrupt)
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "starred"])

        # Should handle KeyboardInterrupt gracefully
        assert result.exit_code == 0
        assert "Browser closed" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_api_error(self, mock_browser_class, mock_client_class, runner):
        """Test API error handling in browse starred."""
        from mygh.exceptions import APIError

        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=APIError("API Error"))
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "starred"])

        # Should handle API error properly
        assert result.exit_code == 1
        assert "API error: API Error" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    @patch("mygh.cli.browse.RepositoryBrowser")
    def test_browse_starred_mygh_exception(self, mock_browser_class, mock_client_class, runner):
        """Test MyGH exception handling in browse starred."""
        from mygh.exceptions import MyGHException

        # Setup mocks
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client_class.return_value.__aexit__.return_value = None

        mock_browser = MagicMock()
        mock_browser.run_async = AsyncMock(side_effect=MyGHException("Custom error"))
        mock_browser_class.return_value = mock_browser

        # Run command
        result = runner.invoke(app, ["browse", "starred"])

        # Should handle MyGH exception properly
        assert result.exit_code == 1
        assert "Error: Custom error" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    def test_browse_starred_client_context_error(self, mock_client_class, runner):
        """Test client context manager error in browse starred."""
        # Setup mock to raise error on context enter
        mock_client_class.return_value.__aenter__.side_effect = Exception("Connection error")

        # Run command
        result = runner.invoke(app, ["browse", "starred"])

        # Should handle client creation error
        assert result.exit_code == 1
        assert "Error running starred browser: Connection error" in result.stdout

    @patch("mygh.cli.browse.GitHubClient")
    def test_browse_repos_client_context_error(self, mock_client_class, runner):
        """Test client context manager error in browse repos."""
        # Setup mock to raise error on context enter
        mock_client_class.return_value.__aenter__.side_effect = Exception("Connection error")

        # Run command
        result = runner.invoke(app, ["browse", "repos"])

        # Should handle client creation error
        assert result.exit_code == 1
        assert "Error running browser: Connection error" in result.stdout
