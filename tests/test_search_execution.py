"""Tests for actual search command execution to improve coverage."""

import tempfile
from unittest.mock import AsyncMock, patch

import httpx
import pytest
import respx
from typer.testing import CliRunner

from mygh.cli.search import search_app
from mygh.exceptions import APIError, AuthenticationError, MyGHException


class TestSearchExecution:
    """Test actual search command execution for coverage."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def sample_repo_data(self):
        """Sample repository data."""
        return {
            "id": 1,
            "node_id": "MDEwOlJlcG9zaXRvcnkx",
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": False,
            "owner": {
                "login": "owner",
                "id": 1,
                "node_id": "MDQ6VXNlcjE=",
                "avatar_url": "https://github.com/images/error/owner_happy.gif",
                "gravatar_id": "",
                "url": "https://api.github.com/users/owner",
                "html_url": "https://github.com/owner",
                "followers_url": "https://api.github.com/users/owner/followers",
                "following_url": "https://api.github.com/users/owner/following{/other_user}",
                "gists_url": "https://api.github.com/users/owner/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/owner/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/owner/subscriptions",
                "organizations_url": "https://api.github.com/users/owner/orgs",
                "repos_url": "https://api.github.com/users/owner/repos",
                "events_url": "https://api.github.com/users/owner/events{/privacy}",
                "received_events_url": "https://api.github.com/users/owner/received_events",
                "type": "User",
                "site_admin": False,
            },
            "html_url": "https://github.com/owner/test-repo",
            "description": "Test repository",
            "fork": False,
            "url": "https://api.github.com/repos/owner/test-repo",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-06-01T00:00:00Z",
            "pushed_at": "2023-06-01T00:00:00Z",
            "clone_url": "https://github.com/owner/test-repo.git",
            "ssh_url": "git@github.com:owner/test-repo.git",
            "size": 100,
            "stargazers_count": 5,
            "watchers_count": 3,
            "language": "Python",
            "has_issues": True,
            "has_projects": True,
            "has_wiki": True,
            "has_pages": False,
            "has_downloads": True,
            "archived": False,
            "disabled": False,
            "open_issues_count": 2,
            "license": None,
            "forks_count": 1,
            "open_issues": 2,
            "watchers": 3,
            "default_branch": "main",
            "topics": ["python", "testing"],
        }

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data."""
        return {
            "login": "testuser",
            "id": 1,
            "node_id": "MDQ6VXNlcjE=",
            "avatar_url": "https://github.com/images/error/testuser_happy.gif",
            "gravatar_id": "",
            "url": "https://api.github.com/users/testuser",
            "html_url": "https://github.com/testuser",
            "followers_url": "https://api.github.com/users/testuser/followers",
            "following_url": "https://api.github.com/users/testuser/following{/other_user}",
            "gists_url": "https://api.github.com/users/testuser/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/testuser/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/testuser/subscriptions",
            "organizations_url": "https://api.github.com/users/testuser/orgs",
            "repos_url": "https://api.github.com/users/testuser/repos",
            "events_url": "https://api.github.com/users/testuser/events{/privacy}",
            "received_events_url": "https://api.github.com/users/testuser/received_events",
            "type": "User",
            "site_admin": False,
            "name": "Test User",
            "company": "Test Company",
            "location": "Test Location",
            "followers": 10,
            "public_repos": 5,
        }

    @respx.mock
    def test_search_repos_table_execution(self, runner, sample_repo_data):
        """Test actual execution of repos search with table output."""
        search_data = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [sample_repo_data],
        }

        respx.get("https://api.github.com/search/repositories").mock(return_value=httpx.Response(200, json=search_data))

        with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
            result = runner.invoke(search_app, ["repos", "python", "--format", "table"])

        assert result.exit_code == 0
        assert "Repository Search Results" in result.stdout
        assert "owner/test-repo" in result.stdout
        assert "Test repository" in result.stdout
        assert "Python" in result.stdout

    @respx.mock
    def test_search_repos_json_execution(self, runner, sample_repo_data):
        """Test actual execution of repos search with JSON output."""
        search_data = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [sample_repo_data],
        }

        respx.get("https://api.github.com/search/repositories").mock(return_value=httpx.Response(200, json=search_data))

        with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
            result = runner.invoke(search_app, ["repos", "python", "--format", "json"])

        assert result.exit_code == 0
        assert '"total_count": 1' in result.stdout
        assert '"incomplete_results": false' in result.stdout
        assert '"items":' in result.stdout

    @respx.mock
    def test_search_repos_output_file_execution(self, runner, sample_repo_data):
        """Test actual execution of repos search with file output."""
        search_data = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [sample_repo_data],
        }

        respx.get("https://api.github.com/search/repositories").mock(return_value=httpx.Response(200, json=search_data))

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_file = f.name

        try:
            with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
                result = runner.invoke(
                    search_app,
                    ["repos", "python", "--format", "json", "--output", output_file],
                )

            assert result.exit_code == 0
            assert "Results written to" in result.stdout
            assert output_file in result.stdout

            # Verify file contents
            with open(output_file) as f:
                content = f.read()
                assert '"total_count": 1' in content
                assert '"incomplete_results": false' in content
        finally:
            import os

            try:
                os.unlink(output_file)
            except FileNotFoundError:
                pass

    @respx.mock
    def test_search_users_table_execution(self, runner, sample_user_data):
        """Test actual execution of users search with table output."""
        search_data = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [sample_user_data],
        }

        respx.get("https://api.github.com/search/users").mock(return_value=httpx.Response(200, json=search_data))

        with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
            result = runner.invoke(search_app, ["users", "john", "--format", "table"])

        assert result.exit_code == 0
        assert "User Search Results" in result.stdout
        assert "testuser" in result.stdout
        assert "Test User" in result.stdout
        assert "Test Company" in result.stdout

    @respx.mock
    def test_search_users_json_execution(self, runner, sample_user_data):
        """Test actual execution of users search with JSON output."""
        search_data = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [sample_user_data],
        }

        respx.get("https://api.github.com/search/users").mock(return_value=httpx.Response(200, json=search_data))

        with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
            result = runner.invoke(search_app, ["users", "john", "--format", "json"])

        assert result.exit_code == 0
        assert '"total_count": 1' in result.stdout
        assert '"incomplete_results": false' in result.stdout
        assert '"items":' in result.stdout

    @respx.mock
    def test_search_users_output_file_execution(self, runner, sample_user_data):
        """Test actual execution of users search with file output."""
        search_data = {
            "total_count": 1,
            "incomplete_results": False,
            "items": [sample_user_data],
        }

        respx.get("https://api.github.com/search/users").mock(return_value=httpx.Response(200, json=search_data))

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_file = f.name

        try:
            with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
                result = runner.invoke(
                    search_app,
                    ["users", "john", "--format", "json", "--output", output_file],
                )

            assert result.exit_code == 0
            assert "Results written to" in result.stdout
            assert output_file in result.stdout

            # Verify file contents
            with open(output_file) as f:
                content = f.read()
                assert '"total_count": 1' in content
                assert '"incomplete_results": false' in content
        finally:
            import os

            try:
                os.unlink(output_file)
            except FileNotFoundError:
                pass

    def test_search_repos_authentication_error(self, runner):
        """Test repos search with authentication error."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_repositories.side_effect = AuthenticationError("Invalid token")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["repos", "python"])

        assert result.exit_code == 1
        assert "Authentication error: Invalid token" in result.stdout
        assert "To authenticate:" in result.stdout
        assert "Set GITHUB_TOKEN environment variable" in result.stdout

    def test_search_repos_api_error(self, runner):
        """Test repos search with API error."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_repositories.side_effect = APIError("API error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["repos", "python"])

        assert result.exit_code == 1
        assert "API error: API error" in result.stdout

    def test_search_repos_mygh_exception(self, runner):
        """Test repos search with MyGH exception."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_repositories.side_effect = MyGHException("MyGH error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["repos", "python"])

        assert result.exit_code == 1
        assert "Error: MyGH error" in result.stdout

    def test_search_repos_keyboard_interrupt(self, runner):
        """Test repos search with keyboard interrupt."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_repositories.side_effect = KeyboardInterrupt()
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["repos", "python"])

        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout

    def test_search_repos_unexpected_error(self, runner):
        """Test repos search with unexpected error."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_repositories.side_effect = ValueError("Unexpected error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["repos", "python"])

        assert result.exit_code == 1
        assert "Unexpected error: Unexpected error" in result.stdout

    def test_search_users_authentication_error(self, runner):
        """Test users search with authentication error."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_users.side_effect = AuthenticationError("Invalid token")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["users", "john"])

        assert result.exit_code == 1
        assert "Authentication error: Invalid token" in result.stdout
        assert "To authenticate:" in result.stdout
        assert "Set GITHUB_TOKEN environment variable" in result.stdout

    def test_search_users_api_error(self, runner):
        """Test users search with API error."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_users.side_effect = APIError("API error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["users", "john"])

        assert result.exit_code == 1
        assert "API error: API error" in result.stdout

    def test_search_users_mygh_exception(self, runner):
        """Test users search with MyGH exception."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_users.side_effect = MyGHException("MyGH error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["users", "john"])

        assert result.exit_code == 1
        assert "Error: MyGH error" in result.stdout

    def test_search_users_keyboard_interrupt(self, runner):
        """Test users search with keyboard interrupt."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_users.side_effect = KeyboardInterrupt()
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["users", "john"])

        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout

    def test_search_users_unexpected_error(self, runner):
        """Test users search with unexpected error."""
        with patch("mygh.cli.search.GitHubClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client.search_users.side_effect = ValueError("Unexpected error")
            mock_client_class.return_value = mock_client

            result = runner.invoke(search_app, ["users", "john"])

        assert result.exit_code == 1
        assert "Unexpected error: Unexpected error" in result.stdout

    def test_handle_exceptions_decorator_sync_function(self):
        """Test handle_exceptions decorator with sync function."""
        import typer

        from mygh.cli.search import handle_exceptions

        @handle_exceptions
        def sync_func():
            raise ValueError("Test error")

        with pytest.raises(typer.Exit):
            sync_func()

    def test_handle_exceptions_decorator_async_function(self):
        """Test handle_exceptions decorator with async function."""
        import typer

        from mygh.cli.search import handle_exceptions

        @handle_exceptions
        async def async_func():
            raise ValueError("Test error")

        with pytest.raises(typer.Exit):
            async_func()

    def test_handle_exceptions_decorator_authentication_error(self):
        """Test handle_exceptions decorator with authentication error."""
        import typer

        from mygh.cli.search import handle_exceptions

        @handle_exceptions
        async def func_with_auth_error():
            raise AuthenticationError("Auth error")

        with pytest.raises(typer.Exit):
            func_with_auth_error()

    def test_handle_exceptions_decorator_api_error(self):
        """Test handle_exceptions decorator with API error."""
        import typer

        from mygh.cli.search import handle_exceptions

        @handle_exceptions
        async def func_with_api_error():
            raise APIError("API error")

        with pytest.raises(typer.Exit):
            func_with_api_error()

    def test_handle_exceptions_decorator_mygh_exception(self):
        """Test handle_exceptions decorator with MyGH exception."""
        import typer

        from mygh.cli.search import handle_exceptions

        @handle_exceptions
        async def func_with_mygh_error():
            raise MyGHException("MyGH error")

        with pytest.raises(typer.Exit):
            func_with_mygh_error()

    def test_handle_exceptions_decorator_keyboard_interrupt(self):
        """Test handle_exceptions decorator with keyboard interrupt."""
        import typer

        from mygh.cli.search import handle_exceptions

        @handle_exceptions
        async def func_with_keyboard_interrupt():
            raise KeyboardInterrupt()

        with pytest.raises(typer.Exit):
            func_with_keyboard_interrupt()

    def test_validation_functions_coverage(self):
        """Test validation functions for coverage."""
        import typer

        from mygh.cli.search import (
            validate_order,
            validate_repo_sort,
            validate_user_sort,
        )

        # Test repo sort validation
        with pytest.raises(typer.Exit):
            validate_repo_sort("invalid")

        # Test user sort validation
        with pytest.raises(typer.Exit):
            validate_user_sort("invalid")

        # Test order validation
        with pytest.raises(typer.Exit):
            validate_order("invalid")

        # Test valid cases (should not raise)
        validate_repo_sort(None)
        validate_repo_sort("stars")
        validate_user_sort(None)
        validate_user_sort("followers")
        validate_order("asc")
        validate_order("desc")

    def test_format_validation_execution(self, runner):
        """Test format validation during execution."""
        # Test invalid format for repos
        with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
            result = runner.invoke(search_app, ["repos", "python", "--format", "invalid"])

        assert result.exit_code == 1
        assert "Invalid format: invalid" in result.stdout
        assert "Available formats: table, json" in result.stdout

        # Test invalid format for users
        with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
            result = runner.invoke(search_app, ["users", "john", "--format", "invalid"])

        assert result.exit_code == 1
        assert "Invalid format: invalid" in result.stdout
        assert "Available formats: table, json" in result.stdout
