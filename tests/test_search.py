"""Tests for the search CLI commands."""

from unittest.mock import patch

from typer.testing import CliRunner

from mygh.cli.main import app


class TestSearchCLI:
    """Test the search CLI commands."""

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
        sort_options = ["stars", "forks", "help-wanted-issues", "updated"]

        for sort_option in sort_options:
            runner = CliRunner()
            result = runner.invoke(
                app, ["search", "repos", "python", "--sort", sort_option]
            )

            assert result.exit_code == 0

        assert mock_asyncio_run.call_count == len(sort_options)

    @patch("mygh.cli.search.asyncio.run")
    def test_search_repos_all_order_options(self, mock_asyncio_run):
        """Test repository search with all valid order options."""
        order_options = ["asc", "desc"]

        for order_option in order_options:
            runner = CliRunner()
            result = runner.invoke(
                app, ["search", "repos", "python", "--order", order_option]
            )

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
        result = runner.invoke(
            app, ["search", "repos", "python", "--output", "repos.json"]
        )

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
        sort_options = ["followers", "repositories", "joined"]

        for sort_option in sort_options:
            runner = CliRunner()
            result = runner.invoke(
                app, ["search", "users", "john", "--sort", sort_option]
            )

            assert result.exit_code == 0

        assert mock_asyncio_run.call_count == len(sort_options)

    @patch("mygh.cli.search.asyncio.run")
    def test_search_users_all_order_options(self, mock_asyncio_run):
        """Test user search with all valid order options."""
        order_options = ["asc", "desc"]

        for order_option in order_options:
            runner = CliRunner()
            result = runner.invoke(
                app, ["search", "users", "john", "--order", order_option]
            )

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
        result = runner.invoke(
            app, ["search", "users", "john", "--output", "users.json"]
        )

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
        result = runner.invoke(
            app, ["search", "repos", "python", "--format", "invalid"]
        )

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
        result = runner.invoke(
            app, ["search", "users", "location:London followers:>100"]
        )

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
        runner = CliRunner(env={"NO_COLOR": "1"})
        result = runner.invoke(app, ["search", "repos", "--help"])

        assert result.exit_code == 0
        # Check for key help text components
        help_text = result.stdout
        assert "--sort" in help_text
        assert "--order" in help_text
        assert "--limit" in help_text
        assert "--format" in help_text
        assert "--output" in help_text

    def test_help_text_completeness_users(self):
        """Test that users search help text contains useful information."""
        runner = CliRunner(env={"NO_COLOR": "1"})
        result = runner.invoke(app, ["search", "users", "--help"])

        assert result.exit_code == 0
        # Check for key help text components
        help_text = result.stdout
        assert "--sort" in help_text
        assert "--order" in help_text
        assert "--limit" in help_text
        assert "--format" in help_text
        assert "--output" in help_text
