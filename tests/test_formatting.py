"""Tests for output formatting utilities."""

from datetime import datetime, timezone
from unittest.mock import patch

from rich.table import Table
from rich.text import Text

from mygh.api.models import GitHubGist, GitHubIssue, GitHubUser
from mygh.utils.formatting import (
    calculate_days_since_commit,
    format_csv_repos,
    format_csv_starred_repos,
    format_datetime,
    format_gist_table,
    format_issue_table,
    format_json,
    format_repo_table,
    format_starred_repo_table,
    format_user_info,
    format_user_table,
    get_commit_age_style,
    print_output,
)


class TestDateTimeFormatting:
    """Test datetime formatting functions."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        dt = datetime(2023, 6, 22, 15, 30, 45, tzinfo=timezone.utc)
        result = format_datetime(dt)
        assert result == "2023-06-22 15:30:45"

    def test_calculate_days_since_commit_today(self, frozen_time):
        """Test days calculation for today."""
        # Same day as frozen time
        pushed_at = datetime(2023, 6, 22, 10, 0, 0, tzinfo=timezone.utc)
        result = calculate_days_since_commit(pushed_at)
        assert result == "Today"

    def test_calculate_days_since_commit_one_day(self, frozen_time):
        """Test days calculation for one day ago."""
        pushed_at = datetime(2023, 6, 21, 10, 0, 0, tzinfo=timezone.utc)
        result = calculate_days_since_commit(pushed_at)
        assert result == "1 day"

    def test_calculate_days_since_commit_multiple_days(self, frozen_time):
        """Test days calculation for multiple days ago."""
        pushed_at = datetime(2023, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        result = calculate_days_since_commit(pushed_at)
        assert result == "7 days"

    def test_calculate_days_since_commit_none(self):
        """Test days calculation with None."""
        result = calculate_days_since_commit(None)
        assert result == "N/A"

    def test_calculate_days_since_commit_naive_datetime(self, frozen_time):
        """Test days calculation with naive datetime."""
        # Naive datetime should be treated as UTC
        pushed_at = datetime(2023, 6, 20, 10, 0, 0)  # No timezone
        result = calculate_days_since_commit(pushed_at)
        assert result == "2 days"

    def test_get_commit_age_style_today(self, frozen_time):
        """Test commit age styling for today."""
        pushed_at = datetime(2023, 6, 22, 10, 0, 0, tzinfo=timezone.utc)
        result = get_commit_age_style(pushed_at)
        assert isinstance(result, Text)
        assert str(result) == "Today"
        assert result.style == "green"

    def test_get_commit_age_style_one_day(self, frozen_time):
        """Test commit age styling for one day."""
        pushed_at = datetime(2023, 6, 21, 10, 0, 0, tzinfo=timezone.utc)
        result = get_commit_age_style(pushed_at)
        assert str(result) == "1 day"
        assert result.style == "green"

    def test_get_commit_age_style_week(self, frozen_time):
        """Test commit age styling for within a week."""
        pushed_at = datetime(2023, 6, 18, 10, 0, 0, tzinfo=timezone.utc)  # 4 days
        result = get_commit_age_style(pushed_at)
        assert str(result) == "4 days"
        assert result.style == "yellow"

    def test_get_commit_age_style_month(self, frozen_time):
        """Test commit age styling for within a month."""
        pushed_at = datetime(2023, 6, 7, 10, 0, 0, tzinfo=timezone.utc)  # 15 days
        result = get_commit_age_style(pushed_at)
        assert str(result) == "15 days"
        assert result.style == "orange3"

    def test_get_commit_age_style_year(self, frozen_time):
        """Test commit age styling for within a year."""
        pushed_at = datetime(2023, 4, 22, 10, 0, 0, tzinfo=timezone.utc)  # ~60 days
        result = get_commit_age_style(pushed_at)
        assert str(result) == "61 days"
        assert result.style == "red"

    def test_get_commit_age_style_very_old(self, frozen_time):
        """Test commit age styling for very old commits."""
        pushed_at = datetime(2021, 6, 22, 10, 0, 0, tzinfo=timezone.utc)  # 2 years
        result = get_commit_age_style(pushed_at)
        assert str(result) == "730 days"
        assert result.style == "dim red"

    def test_get_commit_age_style_none(self):
        """Test commit age styling with None."""
        result = get_commit_age_style(None)
        assert str(result) == "N/A"
        assert result.style == "dim"


class TestTableFormatting:
    """Test table formatting functions."""

    def test_format_user_table(self, sample_user):
        """Test user table formatting."""
        users = [sample_user]
        table = format_user_table(users)

        assert isinstance(table, Table)
        assert table.title == "GitHub Users"
        assert len(table.columns) == 6
        assert len(table.rows) == 1

    def test_format_user_table_empty(self):
        """Test user table formatting with empty list."""
        table = format_user_table([])
        assert isinstance(table, Table)
        assert len(table.rows) == 0

    def test_format_repo_table(self, sample_repo):
        """Test repository table formatting."""
        repos = [sample_repo]
        table = format_repo_table(repos)

        assert isinstance(table, Table)
        assert table.title == "GitHub Repositories"
        assert len(table.columns) == 6
        assert len(table.rows) == 1

    def test_format_starred_repo_table(self, sample_repo):
        """Test starred repository table formatting."""
        repos = [sample_repo]
        table = format_starred_repo_table(repos)

        assert isinstance(table, Table)
        assert table.title == "Starred GitHub Repositories"
        assert len(table.columns) == 6  # Including Last Commit column
        assert len(table.rows) == 1

    def test_format_starred_repo_table_with_long_description(self, sample_repo):
        """Test starred repository table with long description."""
        sample_repo.description = "A" * 50  # Very long description
        repos = [sample_repo]
        table = format_starred_repo_table(repos)

        # Description should be truncated
        assert len(table.rows) == 1
        # Just check that table was created successfully with truncated content

    def test_format_starred_repo_table_with_long_url(self, sample_repo):
        """Test starred repository table with long URL."""
        sample_repo.html_url = "https://github.com/" + "a" * 50 + "/repo"
        repos = [sample_repo]
        table = format_starred_repo_table(repos)

        # Just check that table was created successfully
        assert len(table.rows) == 1

    def test_format_gist_table(self, sample_user):
        """Test gist table formatting."""
        gist = GitHubGist(
            id="abc123",
            description="Test gist",
            public=True,
            created_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            html_url="https://gist.github.com/testuser/abc123",
            files={"test.py": {}},
            owner=sample_user,
        )

        gists = [gist]
        table = format_gist_table(gists)

        assert isinstance(table, Table)
        assert table.title == "GitHub Gists"
        assert len(table.columns) == 5
        assert len(table.rows) == 1

    def test_format_issue_table(self, sample_user):
        """Test issue table formatting."""
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
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            closed_at=None,
            html_url="https://github.com/testuser/test-repo/issues/1",
        )

        issues = [issue]
        table = format_issue_table(issues)

        assert isinstance(table, Table)
        assert table.title == "GitHub Issues"
        assert len(table.columns) == 5
        assert len(table.rows) == 1

    def test_format_issue_table_with_long_title(self, sample_user):
        """Test issue table with long title."""
        issue = GitHubIssue(
            id=11111,
            number=1,
            title="A" * 60,  # Very long title
            body="This is a test issue",
            state="open",
            user=sample_user,
            assignee=None,
            assignees=[],
            labels=[],
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            closed_at=None,
            html_url="https://github.com/testuser/test-repo/issues/1",
        )

        issues = [issue]
        table = format_issue_table(issues)

        # Just check that table was created successfully
        assert len(table.rows) == 1


class TestUserInfoFormatting:
    """Test user info formatting."""

    def test_format_user_info_full_data(self, sample_user):
        """Test user info formatting with full data."""
        with patch("mygh.utils.formatting.console") as mock_console:
            format_user_info(sample_user)

            # Should call print at least once
            assert mock_console.print.call_count >= 1

    def test_format_user_info_minimal_data(self):
        """Test user info formatting with minimal data."""
        user = GitHubUser(
            id=12345,
            login="testuser",
            avatar_url="https://avatars.example.com/testuser",
            html_url="https://github.com/testuser",
        )

        with patch("mygh.utils.formatting.console") as mock_console:
            format_user_info(user)

            # Should still call print
            assert mock_console.print.call_count == 2

    def test_format_user_info_with_none_values(self):
        """Test user info formatting with None values."""
        user = GitHubUser(
            id=12345,
            login="testuser",
            avatar_url="https://avatars.example.com/testuser",
            html_url="https://github.com/testuser",
            public_repos=None,
            public_gists=None,
            followers=None,
            following=None,
            created_at=None,
        )

        with patch("mygh.utils.formatting.console") as mock_console:
            format_user_info(user)

            # Should still work with None values
            assert mock_console.print.call_count == 2


class TestJSONFormatting:
    """Test JSON formatting."""

    def test_format_json_dict(self):
        """Test JSON formatting with dictionary."""
        data = {"key": "value", "number": 42}
        result = format_json(data)

        assert '"key": "value"' in result
        assert '"number": 42' in result

    def test_format_json_pydantic_model(self, sample_user):
        """Test JSON formatting with Pydantic model."""
        result = format_json(sample_user)
        assert '"login": "testuser"' in result
        assert '"id": 12345' in result

    def test_format_json_list_of_models(self, sample_user):
        """Test JSON formatting with list of Pydantic models."""
        users = [sample_user]
        result = format_json(users)
        assert '"login": "testuser"' in result
        assert result.startswith("[")
        assert result.endswith("]")


class TestCSVFormatting:
    """Test CSV formatting."""

    def test_format_csv_repos(self, sample_repo):
        """Test CSV formatting for repositories."""
        repos = [sample_repo]
        result = format_csv_repos(repos)

        lines = result.split("\n")
        assert lines[0] == "name,description,language,stars,forks,updated_at,html_url"
        assert "test-repo" in lines[1]
        assert "Python" in lines[1]
        assert "42" in lines[1]

    def test_format_csv_starred_repos(self, sample_repo):
        """Test CSV formatting for starred repositories."""
        repos = [sample_repo]
        result = format_csv_starred_repos(repos)

        lines = result.split("\n")
        header = lines[0]
        expected_header = (
            "owner,name,full_name,description,language,stars,"
            "days_since_last_commit,pushed_at,html_url"
        )
        assert expected_header == header
        assert "testuser" in lines[1]
        assert "test-repo" in lines[1]

    def test_format_csv_repos_with_special_chars(self, sample_repo):
        """Test CSV formatting with special characters."""
        sample_repo.description = 'Description with "quotes" and \n newlines'
        repos = [sample_repo]
        result = format_csv_repos(repos)

        # Quotes should be escaped and newlines replaced
        assert 'Description with ""quotes"" and   newlines' in result

    def test_format_csv_starred_repos_with_none_values(self, sample_repo):
        """Test CSV formatting with None values."""
        sample_repo.description = None
        sample_repo.language = None
        sample_repo.pushed_at = None
        repos = [sample_repo]
        result = format_csv_starred_repos(repos)

        lines = result.split("\n")
        # Should handle None values gracefully
        assert '"",' in lines[1]  # Empty description
        assert '"N/A"' in lines[1]  # N/A for days since commit


class TestPrintOutput:
    """Test print_output function."""

    def test_print_output_user_table(self, sample_user):
        """Test print output for user (table format)."""
        with patch("mygh.utils.formatting.format_user_info") as mock_format:
            print_output(sample_user, "table")
            mock_format.assert_called_once_with(sample_user)

    def test_print_output_repos_table(self, sample_repo):
        """Test print output for repositories (table format)."""
        repos = [sample_repo]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(repos, "table")
            mock_console.print.assert_called_once()

    def test_print_output_starred_repos_table(self, sample_repo):
        """Test print output for starred repositories (table format)."""
        repos = [sample_repo]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(repos, "table", is_starred=True)
            mock_console.print.assert_called_once()

    def test_print_output_json_format(self, sample_user):
        """Test print output in JSON format."""
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(sample_user, "json")
            mock_console.print.assert_called_once()

            # Check that JSON was printed
            call_args = mock_console.print.call_args[0][0]
            assert '"login": "testuser"' in call_args

    def test_print_output_csv_format(self, sample_repo):
        """Test print output in CSV format."""
        repos = [sample_repo]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(repos, "csv")
            mock_console.print.assert_called_once()

            # Check that CSV header was printed
            call_args = mock_console.print.call_args[0][0]
            assert "name,description" in call_args

    def test_print_output_csv_starred_format(self, sample_repo):
        """Test print output in CSV format for starred repos."""
        repos = [sample_repo]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(repos, "csv", is_starred=True)
            mock_console.print.assert_called_once()

            # Check that starred CSV header was printed
            call_args = mock_console.print.call_args[0][0]
            assert "owner,name,full_name" in call_args

    def test_print_output_to_file(self, sample_repo, tmp_path):
        """Test print output to file."""
        repos = [sample_repo]
        output_file = tmp_path / "test_output.csv"

        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(repos, "csv", str(output_file))

            # Should print confirmation message
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert "Output saved to" in call_args

            # File should exist and contain data
            assert output_file.exists()
            content = output_file.read_text()
            assert "test-repo" in content

    def test_print_output_table_to_file_warning(self, sample_repo):
        """Test warning when trying to save table format to file."""
        repos = [sample_repo]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(repos, "table", "output.txt")

            # Should print warning about table format
            mock_console.print.assert_called()
            call_args = mock_console.print.call_args[0][0]
            assert "Table format cannot be saved to file" in call_args

    def test_print_output_empty_list(self):
        """Test print output with empty list."""
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([], "table")
            mock_console.print.assert_called_once_with("No data to display")

    def test_print_output_non_repo_data(self):
        """Test print output with non-repository data."""
        data = {"key": "value"}
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(data, "table")
            mock_console.print.assert_called_once_with("No data to display")
