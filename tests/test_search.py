"""Tests for the search CLI commands."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from mygh.cli.main import app


def create_safe_asyncio_run_mock():
    """Create a safe mock for asyncio.run that properly closes coroutines."""

    def close_coroutine(coro):
        if asyncio.iscoroutine(coro):
            coro.close()
        return None

    mock = MagicMock(side_effect=close_coroutine)
    return mock


class TestSearchCLI:
    """Test the search CLI commands."""

    @pytest.fixture(autouse=True)
    def setup_coroutine_cleanup(self):
        """Automatically cleanup coroutines for all tests."""
        # This fixture runs for all tests in this class to ensure
        # proper coroutine cleanup and avoid RuntimeWarnings
        pass

    def test_search_help(self):
        """Test search command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "--help"])
        assert result.exit_code == 0
        assert "Advanced search capabilities" in result.stdout

    def test_search_repos_help(self):
        """Test search repos command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "--help"])
        assert result.exit_code == 0
        assert "Search repositories" in result.stdout

    def test_search_users_help(self):
        """Test search users command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "--help"])
        assert result.exit_code == 0
        assert "Search users" in result.stdout

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_basic(self, mock_asyncio_run):
        """Test basic repository search."""
        mock_asyncio_run.side_effect = create_safe_asyncio_run_mock().side_effect

        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_with_sort(self, mock_asyncio_run):
        """Test repository search with sort option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--sort", "stars"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_with_order(self, mock_asyncio_run):
        """Test repository search with order option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--order", "asc"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_with_limit(self, mock_asyncio_run):
        """Test repository search with limit option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--limit", "10"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_all_sort_options(self, mock_asyncio_run):
        """Test repository search with all valid sort options."""
        import asyncio

        # Configure mock to close coroutines properly to avoid unawaited warnings
        def close_coroutine(coro):
            if asyncio.iscoroutine(coro):
                coro.close()
            return None

        mock_asyncio_run.side_effect = close_coroutine

        sort_options = ["stars", "forks", "help-wanted-issues", "updated"]

        for sort_option in sort_options:
            runner = CliRunner()
            result = runner.invoke(app, ["search", "repos", "python", "--sort", sort_option])

            assert result.exit_code == 0

        assert mock_asyncio_run.call_count == len(sort_options)

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_all_order_options(self, mock_asyncio_run):
        """Test repository search with all valid order options."""
        import asyncio

        # Configure mock to close coroutines properly to avoid unawaited warnings
        def close_coroutine(coro):
            if asyncio.iscoroutine(coro):
                coro.close()
            return None

        mock_asyncio_run.side_effect = close_coroutine

        order_options = ["asc", "desc"]

        for order_option in order_options:
            runner = CliRunner()
            result = runner.invoke(app, ["search", "repos", "python", "--order", order_option])

            assert result.exit_code == 0

        assert mock_asyncio_run.call_count == len(order_options)

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_with_format_json(self, mock_asyncio_run):
        """Test repository search with JSON format."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--format", "json"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_with_output_file(self, mock_asyncio_run):
        """Test repository search with output file."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--output", "repos.json"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_all_options(self, mock_asyncio_run):
        """Test repository search with all options."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "search",
                "repos",
                "python",
                "--sort",
                "stars",
                "--order",
                "desc",
                "--limit",
                "5",
                "--format",
                "json",
                "--output",
                "search_results.json",
            ],
        )

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_basic(self, mock_asyncio_run):
        """Test basic user search."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_with_sort(self, mock_asyncio_run):
        """Test user search with sort option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--sort", "followers"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_with_order(self, mock_asyncio_run):
        """Test user search with order option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--order", "asc"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_with_limit(self, mock_asyncio_run):
        """Test user search with limit option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--limit", "15"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_all_sort_options(self, mock_asyncio_run):
        """Test user search with all valid sort options."""
        import asyncio

        # Configure mock to close coroutines properly to avoid unawaited warnings
        def close_coroutine(coro):
            if asyncio.iscoroutine(coro):
                coro.close()
            return None

        mock_asyncio_run.side_effect = close_coroutine

        sort_options = ["followers", "repositories", "joined"]

        for sort_option in sort_options:
            runner = CliRunner()
            result = runner.invoke(app, ["search", "users", "john", "--sort", sort_option])

            assert result.exit_code == 0

        assert mock_asyncio_run.call_count == len(sort_options)

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_all_order_options(self, mock_asyncio_run):
        """Test user search with all valid order options."""
        import asyncio

        # Configure mock to close coroutines properly to avoid unawaited warnings
        def close_coroutine(coro):
            if asyncio.iscoroutine(coro):
                coro.close()
            return None

        mock_asyncio_run.side_effect = close_coroutine

        order_options = ["asc", "desc"]

        for order_option in order_options:
            runner = CliRunner()
            result = runner.invoke(app, ["search", "users", "john", "--order", order_option])

            assert result.exit_code == 0

        assert mock_asyncio_run.call_count == len(order_options)

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_with_format_json(self, mock_asyncio_run):
        """Test user search with JSON format."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--format", "json"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_with_output_file(self, mock_asyncio_run):
        """Test user search with output file."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--output", "users.json"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_all_options(self, mock_asyncio_run):
        """Test user search with all options."""
        runner = CliRunner()
        result = runner.invoke(
            app,
            [
                "search",
                "users",
                "john",
                "--sort",
                "followers",
                "--order",
                "desc",
                "--limit",
                "8",
                "--format",
                "json",
                "--output",
                "user_search.json",
            ],
        )

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    def test_search_repos_invalid_sort(self):
        """Test repository search with invalid sort option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--sort", "invalid"])

        # Should exit with error due to invalid choice
        assert result.exit_code != 0

    def test_search_users_invalid_sort(self):
        """Test user search with invalid sort option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--sort", "invalid"])

        # Should exit with error due to invalid choice
        assert result.exit_code != 0

    def test_search_repos_invalid_order(self):
        """Test repository search with invalid order option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--order", "invalid"])

        # Should exit with error due to invalid choice
        assert result.exit_code != 0

    def test_search_users_invalid_order(self):
        """Test user search with invalid order option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--order", "invalid"])

        # Should exit with error due to invalid choice
        assert result.exit_code != 0

    def test_search_repos_invalid_format(self):
        """Test repository search with invalid format option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--format", "invalid"])

        # Should exit with error due to invalid choice
        assert result.exit_code != 0

    def test_search_users_invalid_format(self):
        """Test user search with invalid format option."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--format", "invalid"])

        # Should exit with error due to invalid choice
        assert result.exit_code != 0

    def test_search_repos_negative_limit(self):
        """Test repository search with negative limit."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--limit", "-1"])

        # Should exit with error due to invalid value
        assert result.exit_code != 0

    def test_search_users_negative_limit(self):
        """Test user search with negative limit."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--limit", "-1"])

        # Should exit with error due to invalid value
        assert result.exit_code != 0

    def test_search_repos_zero_limit(self):
        """Test repository search with zero limit."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--limit", "0"])

        # Should exit with error due to invalid value
        assert result.exit_code != 0

    def test_search_users_zero_limit(self):
        """Test user search with zero limit."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--limit", "0"])

        # Should exit with error due to invalid value
        assert result.exit_code != 0

    @patch("mygh.cli.search.asyncio.run")
    def test_search_complex_query_repos(self, mock_asyncio_run):
        """Test repository search with complex query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "language:python stars:>1000"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_complex_query_users(self, mock_asyncio_run):
        """Test user search with complex query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "location:London followers:>100"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_empty_query_repos(self, mock_asyncio_run):
        """Test repository search with empty query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", ""])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_empty_query_users(self, mock_asyncio_run):
        """Test user search with empty query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", ""])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_quoted_query_repos(self, mock_asyncio_run):
        """Test repository search with quoted query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", '"machine learning"'])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_quoted_query_users(self, mock_asyncio_run):
        """Test user search with quoted query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", '"John Smith"'])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_large_limit_repos(self, mock_asyncio_run):
        """Test repository search with large limit."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "python", "--limit", "1000"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_large_limit_users(self, mock_asyncio_run):
        """Test user search with large limit."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "users", "john", "--limit", "1000"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_special_characters_query(self, mock_asyncio_run):
        """Test search with special characters in query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "test+repo-name_with.special"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    @patch("mygh.cli.search.asyncio.run")
    def test_search_unicode_query(self, mock_asyncio_run):
        """Test search with unicode characters in query."""
        runner = CliRunner()
        result = runner.invoke(app, ["search", "repos", "pythön"])

        assert result.exit_code == 0
        mock_asyncio_run.assert_called_once()

    def test_help_text_completeness_repos(self):
        """Test that repos search help text contains useful information."""
        import re

        runner = CliRunner(env={"NO_COLOR": "1"})
        result = runner.invoke(app, ["search", "repos", "--help"])

        assert result.exit_code == 0
        # Strip ANSI escape codes for robust testing
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_text = ansi_escape.sub("", result.stdout)

        assert "--sort" in clean_text
        assert "--order" in clean_text
        assert "--limit" in clean_text
        assert "--format" in clean_text
        assert "--output" in clean_text

    def test_help_text_completeness_users(self):
        """Test that users search help text contains useful information."""
        import re

        runner = CliRunner(env={"NO_COLOR": "1"})
        result = runner.invoke(app, ["search", "users", "--help"])

        assert result.exit_code == 0
        # Strip ANSI escape codes for robust testing
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean_text = ansi_escape.sub("", result.stdout)

        assert "--sort" in clean_text
        assert "--order" in clean_text
        assert "--limit" in clean_text
        assert "--format" in clean_text
        assert "--output" in clean_text
