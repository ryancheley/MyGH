"""Tests for CLI commands."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from mygh.api.models import GitHubGist, GitHubIssue
from mygh.cli.main import app
from mygh.exceptions import APIError, AuthenticationError


class TestMainCLI:
    """Test main CLI application."""

    def test_help_command(self, cli_runner):
        """Test main help command."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "A comprehensive GitHub CLI tool" in result.stdout
        assert "user" in result.stdout
        assert "repos" in result.stdout
        assert "config" in result.stdout

    def test_version_functionality(self):
        """Test version functionality directly."""
        import typer

        from mygh import __version__
        from mygh.cli.main import main

        # Test version flag logic - just pass None for context since it's not used
        with patch("mygh.cli.main.console") as mock_console:
            with pytest.raises(typer.Exit):
                main(None, version=True)

            # Check that version was printed
            mock_console.print.assert_called_once_with(f"mygh version {__version__}")

    def test_version_import(self):
        """Test that version can be imported."""
        from mygh import __version__

        assert __version__ == "0.1.0"

    def test_exception_decorator_sync_function(self):
        """Test exception decorator with sync function."""
        import typer

        from mygh.cli.main import handle_exceptions
        from mygh.exceptions import AuthenticationError

        @handle_exceptions
        def sync_func():
            raise AuthenticationError("Test auth error")

        with pytest.raises(typer.Exit) as exc_info:
            sync_func()
        assert exc_info.value.exit_code == 1

    def test_exception_decorator_api_error(self):
        """Test exception decorator with API error."""
        import typer

        from mygh.cli.main import handle_exceptions
        from mygh.exceptions import APIError

        @handle_exceptions
        def sync_func():
            raise APIError("Test API error")

        with pytest.raises(typer.Exit) as exc_info:
            sync_func()
        assert exc_info.value.exit_code == 1

    def test_exception_decorator_mygh_exception(self):
        """Test exception decorator with MyGH exception."""
        import typer

        from mygh.cli.main import handle_exceptions
        from mygh.exceptions import MyGHException

        @handle_exceptions
        def sync_func():
            raise MyGHException("Test MyGH error")

        with pytest.raises(typer.Exit) as exc_info:
            sync_func()
        assert exc_info.value.exit_code == 1

    def test_exception_decorator_keyboard_interrupt(self):
        """Test exception decorator with keyboard interrupt."""
        import typer

        from mygh.cli.main import handle_exceptions

        @handle_exceptions
        def sync_func():
            raise KeyboardInterrupt()

        with pytest.raises(typer.Exit) as exc_info:
            sync_func()
        assert exc_info.value.exit_code == 0

    def test_exception_decorator_unexpected_error(self):
        """Test exception decorator with unexpected error."""
        import typer

        from mygh.cli.main import handle_exceptions

        @handle_exceptions
        def sync_func():
            raise ValueError("Unexpected error")

        with pytest.raises(typer.Exit) as exc_info:
            sync_func()
        assert exc_info.value.exit_code == 1

    def test_exception_decorator_async_function(self):
        """Test exception decorator with async function."""
        import typer

        from mygh.cli.main import handle_exceptions
        from mygh.exceptions import AuthenticationError

        @handle_exceptions
        async def async_func():
            raise AuthenticationError("Test async auth error")

        with pytest.raises(typer.Exit) as exc_info:
            async_func()
        assert exc_info.value.exit_code == 1

    def test_config_list_command(self, cli_runner, temp_config_dir):
        """Test config list command."""
        result = cli_runner.invoke(app, ["config", "list"])

        assert result.exit_code == 0
        assert "Current Configuration:" in result.stdout
        # Check that output-format appears with either table or json
        # (depends on config state)
        assert "output-format:" in result.stdout
        assert "default-per-page: 30" in result.stdout

    def test_config_set_command(self, cli_runner, temp_config_dir):
        """Test config set command."""
        result = cli_runner.invoke(app, ["config", "set", "output-format", "json"])

        assert result.exit_code == 0
        assert "Set output-format = json" in result.stdout

    def test_config_get_command(self, cli_runner, temp_config_dir):
        """Test config get command."""
        # First set a value
        cli_runner.invoke(app, ["config", "set", "output-format", "json"])

        # Then get it
        result = cli_runner.invoke(app, ["config", "get", "output-format"])

        assert result.exit_code == 0
        assert "output-format: json" in result.stdout

    def test_config_get_nonexistent_key(self, cli_runner, temp_config_dir):
        """Test config get with nonexistent key."""
        result = cli_runner.invoke(app, ["config", "get", "nonexistent-key"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_config_set_invalid_action(self, cli_runner, temp_config_dir):
        """Test config with invalid action."""
        result = cli_runner.invoke(app, ["config", "invalid-action"])

        assert result.exit_code == 1
        assert "Unknown action" in result.stdout

    def test_config_set_missing_value(self, cli_runner, temp_config_dir):
        """Test config set with missing value."""
        result = cli_runner.invoke(app, ["config", "set", "output-format"])

        assert result.exit_code != 0  # Should fail

    def test_config_get_missing_key(self, cli_runner, temp_config_dir):
        """Test config get with missing key."""
        result = cli_runner.invoke(app, ["config", "get"])

        assert result.exit_code != 0  # Should fail


class TestUserCLI:
    """Test user CLI commands."""

    def test_user_help(self, cli_runner):
        """Test user help command."""
        result = cli_runner.invoke(app, ["user", "--help"])

        assert result.exit_code == 0
        assert "User-related commands" in result.stdout
        assert "info" in result.stdout
        assert "starred" in result.stdout
        assert "gists" in result.stdout

    def test_user_info_help(self, cli_runner):
        """Test user info help command."""
        from .conftest import strip_ansi_codes

        result = cli_runner.invoke(app, ["user", "info", "--help"])
        clean_output = strip_ansi_codes(result.stdout)

        assert result.exit_code == 0
        assert "Get user information" in clean_output
        assert "username" in clean_output
        assert "--format" in clean_output
        assert "--output" in clean_output

    @patch("mygh.cli.user.GitHubClient")
    def test_user_info_command(
        self, mock_client_class, cli_runner, mock_github_token, sample_user
    ):
        """Test user info command."""
        # Mock the client and its methods
        mock_client = AsyncMock()
        mock_client.get_user.return_value = sample_user
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.user.print_output") as mock_print:
            result = cli_runner.invoke(app, ["user", "info"])

            assert result.exit_code == 0
            mock_client.get_user.assert_called_once_with(None)
            mock_print.assert_called_once_with(sample_user, "table", None)

    @patch("mygh.cli.user.GitHubClient")
    def test_user_info_with_username(
        self, mock_client_class, cli_runner, mock_github_token, sample_user
    ):
        """Test user info command with username."""
        mock_client = AsyncMock()
        mock_client.get_user.return_value = sample_user
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.user.print_output"):
            result = cli_runner.invoke(app, ["user", "info", "testuser"])

            assert result.exit_code == 0
            mock_client.get_user.assert_called_once_with("testuser")

    @patch("mygh.cli.user.GitHubClient")
    def test_user_info_json_format(
        self, mock_client_class, cli_runner, mock_github_token, sample_user
    ):
        """Test user info command with JSON format."""
        mock_client = AsyncMock()
        mock_client.get_user.return_value = sample_user
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.user.print_output") as mock_print:
            result = cli_runner.invoke(app, ["user", "info", "--format", "json"])

            assert result.exit_code == 0
            mock_print.assert_called_once_with(sample_user, "json", None)

    @patch("mygh.cli.user.GitHubClient")
    def test_user_starred_command(
        self, mock_client_class, cli_runner, mock_github_token, sample_repo
    ):
        """Test user starred command."""
        mock_client = AsyncMock()
        mock_client.get_starred_repos.return_value = [sample_repo]
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.user.print_output") as mock_print:
            result = cli_runner.invoke(app, ["user", "starred", "--limit", "5"])

            assert result.exit_code == 0
            mock_client.get_starred_repos.assert_called()
            mock_print.assert_called_once_with(
                [sample_repo], "table", None, is_starred=True
            )

    @patch("mygh.cli.user.GitHubClient")
    def test_user_starred_with_language(
        self, mock_client_class, cli_runner, mock_github_token, sample_repo
    ):
        """Test user starred command with language filter."""
        mock_client = AsyncMock()
        mock_client.get_starred_repos.return_value = [sample_repo]
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["user", "starred", "--language", "Python"])

        assert result.exit_code == 0
        # Check that language parameter was passed
        call_args = mock_client.get_starred_repos.call_args
        assert call_args.kwargs["language"] == "Python"

    @patch("mygh.cli.user.GitHubClient")
    def test_user_starred_no_results(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test user starred command with no results."""
        mock_client = AsyncMock()
        mock_client.get_starred_repos.return_value = []
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["user", "starred"])

        assert result.exit_code == 0
        assert "No starred repositories found" in result.stdout

    @patch("mygh.cli.user.GitHubClient")
    def test_user_gists_command(
        self, mock_client_class, cli_runner, mock_github_token, sample_user
    ):
        """Test user gists command."""
        gist = GitHubGist(
            id="abc123",
            description="Test gist",
            public=True,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
            html_url="https://gist.github.com/testuser/abc123",
            files={"test.py": {}},
            owner=sample_user,
        )

        mock_client = AsyncMock()
        mock_client.get_user_gists.return_value = [gist]
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.user.print_output") as mock_print:
            result = cli_runner.invoke(app, ["user", "gists"])

            assert result.exit_code == 0
            mock_client.get_user_gists.assert_called_once_with(None)
            mock_print.assert_called_once()

    @patch("mygh.cli.user.GitHubClient")
    def test_user_gists_public_only(
        self, mock_client_class, cli_runner, mock_github_token, sample_user
    ):
        """Test user gists command with public only filter."""
        public_gist = GitHubGist(
            id="public123",
            description="Public gist",
            public=True,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
            html_url="https://gist.github.com/testuser/public123",
            files={"test.py": {}},
            owner=sample_user,
        )

        private_gist = GitHubGist(
            id="private123",
            description="Private gist",
            public=False,
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
            html_url="https://gist.github.com/testuser/private123",
            files={"test.py": {}},
            owner=sample_user,
        )

        mock_client = AsyncMock()
        mock_client.get_user_gists.return_value = [public_gist, private_gist]
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.user.print_output") as mock_print:
            result = cli_runner.invoke(app, ["user", "gists", "--public"])

            assert result.exit_code == 0
            # Should only print public gists
            printed_gists = mock_print.call_args[0][0]
            assert len(printed_gists) == 1
            assert printed_gists[0].public is True

    @patch("mygh.cli.user.GitHubClient")
    def test_user_gists_no_results(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test user gists command with no results."""
        mock_client = AsyncMock()
        mock_client.get_user_gists.return_value = []
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["user", "gists"])

        assert result.exit_code == 0
        assert "No gists found" in result.stdout

    @patch("mygh.cli.user.GitHubClient")
    def test_user_mygh_exception(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test user command with MyGH exception."""
        from mygh.exceptions import MyGHException

        mock_client = AsyncMock()
        mock_client.get_user.side_effect = MyGHException("Custom MyGH error")
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["user", "info"])

        assert result.exit_code == 1
        assert "Error: Custom MyGH error" in result.stdout

    @patch("mygh.cli.user.GitHubClient")
    def test_authentication_error(self, mock_client_class, cli_runner):
        """Test authentication error handling."""
        mock_client = AsyncMock()
        mock_client.get_user.side_effect = AuthenticationError("Invalid token")
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["user", "info"])

        assert result.exit_code == 1
        assert "Authentication error" in result.stdout
        assert "To authenticate:" in result.stdout

    @patch("mygh.cli.user.GitHubClient")
    def test_api_error(self, mock_client_class, cli_runner, mock_github_token):
        """Test API error handling."""
        mock_client = AsyncMock()
        mock_client.get_user.side_effect = APIError("API error occurred")
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["user", "info"])

        assert result.exit_code == 1
        assert "API error" in result.stdout


class TestReposCLI:
    """Test repos CLI commands."""

    def test_repos_help(self, cli_runner):
        """Test repos help command."""
        result = cli_runner.invoke(app, ["repos", "--help"])

        assert result.exit_code == 0
        assert "Repository management commands" in result.stdout
        assert "list" in result.stdout
        assert "info" in result.stdout
        assert "issues" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_list_command(
        self, mock_client_class, cli_runner, mock_github_token, sample_repo
    ):
        """Test repos list command."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.return_value = [sample_repo]
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.repos.print_output") as mock_print:
            result = cli_runner.invoke(app, ["repos", "list"])

            assert result.exit_code == 0
            mock_client.get_user_repos.assert_called()
            mock_print.assert_called_once()

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_list_with_params(
        self, mock_client_class, cli_runner, mock_github_token, sample_repo
    ):
        """Test repos list command with parameters."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.return_value = [sample_repo]
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(
            app,
            ["repos", "list", "--type", "public", "--sort", "created", "--limit", "10"],
        )

        assert result.exit_code == 0
        call_args = mock_client.get_user_repos.call_args
        assert call_args.kwargs["repo_type"] == "public"
        assert call_args.kwargs["sort"] == "created"

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_info_command(
        self, mock_client_class, cli_runner, mock_github_token, sample_repo
    ):
        """Test repos info command."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.return_value = [sample_repo]
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.repos.print_output") as mock_print:
            result = cli_runner.invoke(app, ["repos", "info", "testuser/test-repo"])

            assert result.exit_code == 0
            mock_print.assert_called_once()

    def test_repos_info_invalid_format(self, cli_runner):
        """Test repos info command with invalid repo name format."""
        result = cli_runner.invoke(app, ["repos", "info", "invalid-repo-name"])

        assert result.exit_code == 1
        assert "must be in 'owner/repo' format" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_info_not_found(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test repos info command when repository is not found."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.return_value = []  # No repos found
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["repos", "info", "testuser/nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_issues_command(
        self, mock_client_class, cli_runner, mock_github_token, sample_user
    ):
        """Test repos issues command."""
        issue = GitHubIssue(
            id=11111,
            number=1,
            title="Test issue",
            body="This is a test issue",
            state="open",
            user=sample_user,
            assignee=None,
            assignees=[],
            labels=[],
            created_at=sample_user.created_at,
            updated_at=sample_user.updated_at,
            closed_at=None,
            html_url="https://github.com/testuser/test-repo/issues/1",
        )

        mock_client = AsyncMock()
        mock_client.get_repo_issues.return_value = [issue]
        mock_client_class.return_value = mock_client

        with patch("mygh.cli.repos.print_output") as mock_print:
            result = cli_runner.invoke(app, ["repos", "issues", "testuser/test-repo"])

            assert result.exit_code == 0
            mock_client.get_repo_issues.assert_called()
            mock_print.assert_called_once()

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_issues_with_filters(
        self, mock_client_class, cli_runner, mock_github_token, sample_user
    ):
        """Test repos issues command with filters."""
        mock_client = AsyncMock()
        mock_client.get_repo_issues.return_value = []
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(
            app,
            [
                "repos",
                "issues",
                "testuser/test-repo",
                "--state",
                "closed",
                "--assignee",
                "@me",
                "--labels",
                "bug,help wanted",
            ],
        )

        assert result.exit_code == 0
        call_args = mock_client.get_repo_issues.call_args
        assert call_args.kwargs["state"] == "closed"
        assert call_args.kwargs["assignee"] == "@me"
        assert call_args.kwargs["labels"] == "bug,help wanted"

    def test_repos_issues_invalid_format(self, cli_runner):
        """Test repos issues command with invalid repo name format."""
        result = cli_runner.invoke(app, ["repos", "issues", "invalid-repo-name"])

        assert result.exit_code == 1
        assert "must be in 'owner/repo' format" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_list_no_results(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test repos list command with no results."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.return_value = []
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 0
        assert "No repositories found" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_issues_no_results(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test repos issues command with no results."""
        mock_client = AsyncMock()
        mock_client.get_repo_issues.return_value = []
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["repos", "issues", "testuser/test-repo"])

        assert result.exit_code == 0
        assert "No issues found" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_authentication_error(self, mock_client_class, cli_runner):
        """Test repos command with authentication error."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.side_effect = AuthenticationError("Invalid token")
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 1
        assert "Authentication error" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_mygh_exception(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test repos command with MyGH exception."""
        from mygh.exceptions import MyGHException

        mock_client = AsyncMock()
        mock_client.get_user_repos.side_effect = MyGHException("Custom repos error")
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 1
        assert "Error: Custom repos error" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_keyboard_interrupt(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test repos command with keyboard interrupt."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.side_effect = KeyboardInterrupt()
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout

    @patch("mygh.cli.repos.GitHubClient")
    def test_repos_unexpected_error(
        self, mock_client_class, cli_runner, mock_github_token
    ):
        """Test repos command with unexpected error."""
        mock_client = AsyncMock()
        mock_client.get_user_repos.side_effect = ValueError("Unexpected error")
        mock_client_class.return_value = mock_client

        result = cli_runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 1
        assert "Unexpected error" in result.stdout


class TestCLIIntegration:
    """Test CLI integration and edge cases."""

    def test_keyboard_interrupt_handling(self, cli_runner):
        """Test keyboard interrupt handling."""
        with patch("mygh.cli.user.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_user.side_effect = KeyboardInterrupt()
            mock_client_class.return_value = mock_client

            result = cli_runner.invoke(app, ["user", "info"])

            assert result.exit_code == 0
            assert "Operation cancelled" in result.stdout

    def test_unexpected_error_handling(self, cli_runner, mock_github_token):
        """Test unexpected error handling."""
        with patch("mygh.cli.user.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_user.side_effect = Exception("Unexpected error")
            mock_client_class.return_value = mock_client

            result = cli_runner.invoke(app, ["user", "info"])

            assert result.exit_code == 1
            assert "Unexpected error" in result.stdout

    def test_client_cleanup(self, cli_runner, mock_github_token):
        """Test that client is properly cleaned up."""
        with patch("mygh.cli.user.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_user.return_value = Mock()
            mock_client_class.return_value = mock_client

            with patch("mygh.cli.user.print_output"):
                cli_runner.invoke(app, ["user", "info"])

                # Client should be closed
                mock_client.close.assert_called_once()

    def test_pagination_handling(self, cli_runner, mock_github_token, sample_repo):
        """Test pagination handling in starred repos."""
        with patch("mygh.cli.user.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()

            # Simulate pagination: first call returns 100 repos, second returns 50
            first_batch = [sample_repo] * 100
            second_batch = [sample_repo] * 50
            mock_client.get_starred_repos.side_effect = [first_batch, second_batch]
            mock_client_class.return_value = mock_client

            with patch("mygh.cli.user.print_output") as mock_print:
                result = cli_runner.invoke(app, ["user", "starred", "--limit", "120"])

                assert result.exit_code == 0
                # Should have made two API calls
                assert mock_client.get_starred_repos.call_count == 2
                # Should print exactly 120 repos (trimmed to limit)
                printed_repos = mock_print.call_args[0][0]
                assert len(printed_repos) == 120
