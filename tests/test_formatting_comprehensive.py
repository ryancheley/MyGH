"""Comprehensive tests for formatting to boost coverage."""

import tempfile
from datetime import datetime, timezone
from unittest.mock import patch

from mygh.api.models import GitHubGist, GitHubIssue, GitHubRepo, GitHubUser
from mygh.utils.formatting import (
    calculate_days_since_commit,
    format_csv_repos,
    format_csv_starred_repos,
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


class TestFormattingComprehensive:
    """Comprehensive formatting tests to boost coverage."""

    def test_format_user_table_with_none_values(self):
        """Test user table formatting with None values."""
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
            name=None,
            company=None,
            location=None,
            public_repos=None,
            followers=None,
        )

        table = format_user_table([user])
        assert table.title == "GitHub Users"
        assert len(table.rows) == 1

    def test_format_repo_table_with_none_values(self):
        """Test repo table formatting with None values."""
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        repo = GitHubRepo(
            id=456,
            name="test-repo",
            full_name="testuser/test-repo",
            description=None,  # None description
            private=False,
            fork=False,
            language=None,  # None language
            stargazers_count=0,
            watchers_count=0,
            forks_count=0,
            open_issues_count=0,
            size=100,
            default_branch="main",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            pushed_at=None,  # None pushed_at
            html_url="https://github.com/testuser/test-repo",
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            owner=user,
        )

        table = format_repo_table([repo])
        assert table.title == "GitHub Repositories"
        assert len(table.rows) == 1

    def test_format_starred_repo_table_truncation(self):
        """Test starred repo table with truncation scenarios."""
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        repo = GitHubRepo(
            id=456,
            name="test-repo",
            full_name="testuser/test-repo",
            description="A" * 50,  # Long description
            private=False,
            fork=False,
            language="Python",
            stargazers_count=100,
            watchers_count=50,
            forks_count=10,
            open_issues_count=5,
            size=1000,
            default_branch="main",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            pushed_at=datetime.now(timezone.utc),
            html_url="https://github.com/" + "a" * 50 + "/test-repo",  # Long URL
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            owner=user,
        )

        table = format_starred_repo_table([repo])
        assert table.title == "Starred GitHub Repositories"
        assert len(table.rows) == 1

    def test_format_gist_table_comprehensive(self):
        """Test gist table formatting comprehensively."""
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        # Gist with long description
        gist1 = GitHubGist(
            id="gist123",
            description="A" * 60,  # Long description
            public=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://gist.github.com/testuser/gist123",
            files={"file1.py": {}, "file2.js": {}, "file3.txt": {}},
            owner=user,
        )

        # Gist with None description
        gist2 = GitHubGist(
            id="gist456",
            description=None,
            public=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://gist.github.com/testuser/gist456",
            files={"single.py": {}},
            owner=user,
        )

        table = format_gist_table([gist1, gist2])
        assert table.title == "GitHub Gists"
        assert len(table.rows) == 2

    def test_format_issue_table_comprehensive(self):
        """Test issue table formatting comprehensively."""
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        # Open issue with long title
        issue1 = GitHubIssue(
            id=111,
            number=1,
            title="A" * 60,  # Long title
            body="Issue body",
            state="open",
            user=user,
            assignee=None,
            assignees=[],
            labels=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            closed_at=None,
            html_url="https://github.com/testuser/repo/issues/1",
        )

        # Closed issue
        issue2 = GitHubIssue(
            id=222,
            number=2,
            title="Closed issue",
            body=None,  # None body
            state="closed",
            user=user,
            assignee=user,
            assignees=[user],
            labels=[{"name": "bug", "color": "red"}],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            closed_at=datetime.now(timezone.utc),
            html_url="https://github.com/testuser/repo/issues/2",
        )

        table = format_issue_table([issue1, issue2])
        assert table.title == "GitHub Issues"
        assert len(table.rows) == 2

    def test_format_user_info_comprehensive(self):
        """Test user info formatting with various scenarios."""
        # User with all fields
        user_full = GitHubUser(
            id=123,
            login="testuser",
            name="Test User",
            email="test@example.com",
            bio="This is a bio",
            company="Test Company",
            location="Test Location",
            blog="https://test.example.com",
            public_repos=50,
            public_gists=10,
            followers=100,
            following=75,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        with patch("mygh.utils.formatting.console") as mock_console:
            format_user_info(user_full)
            assert mock_console.print.call_count >= 1

        # User with minimal fields
        user_minimal = GitHubUser(
            id=456,
            login="minimaluser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/minimaluser",
            name=None,
            email=None,
            bio=None,
            company=None,
            location=None,
            blog=None,
            public_repos=None,
            public_gists=None,
            followers=None,
            following=None,
            created_at=None,
            updated_at=None,
        )

        with patch("mygh.utils.formatting.console") as mock_console:
            format_user_info(user_minimal)
            assert mock_console.print.call_count >= 1

    def test_format_json_all_scenarios(self):
        """Test JSON formatting with all data type scenarios."""
        # Test with Pydantic model (newer version)
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        result = format_json(user)
        assert '"login": "testuser"' in result

        # Test with list of Pydantic models
        result = format_json([user])
        assert '"login": "testuser"' in result

        # Test with regular dict
        result = format_json({"key": "value"})
        assert '"key": "value"' in result

        # Test with list of dicts
        result = format_json([{"key": "value"}])
        assert '"key": "value"' in result

    def test_format_csv_comprehensive(self):
        """Test CSV formatting comprehensively."""
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        repo = GitHubRepo(
            id=456,
            name="test-repo",
            full_name="testuser/test-repo",
            description='Description with "quotes" and \n newlines',
            private=False,
            fork=False,
            language="Python",
            stargazers_count=100,
            watchers_count=50,
            forks_count=10,
            open_issues_count=5,
            size=1000,
            default_branch="main",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            pushed_at=datetime.now(timezone.utc),
            html_url="https://github.com/testuser/test-repo",
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            owner=user,
        )

        # Test regular CSV
        result = format_csv_repos([repo])
        assert "name,description,language" in result
        assert "test-repo" in result

        # Test starred CSV
        result = format_csv_starred_repos([repo])
        assert "owner,name,full_name" in result
        assert "testuser" in result

    def test_print_output_all_branches(self):
        """Test print_output hitting all code branches."""
        user = GitHubUser(
            id=123,
            login="testuser",
            avatar_url="https://example.com/avatar",
            html_url="https://github.com/testuser",
        )

        repo = GitHubRepo(
            id=456,
            name="test-repo",
            full_name="testuser/test-repo",
            private=False,
            fork=False,
            language="Python",
            stargazers_count=100,
            watchers_count=50,
            forks_count=10,
            open_issues_count=5,
            size=1000,
            default_branch="main",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            pushed_at=datetime.now(timezone.utc),
            html_url="https://github.com/testuser/test-repo",
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            owner=user,
        )

        gist = GitHubGist(
            id="gist123",
            description="Test gist",
            public=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            html_url="https://gist.github.com/testuser/gist123",
            files={"test.py": {}},
            owner=user,
        )

        issue = GitHubIssue(
            id=111,
            number=1,
            title="Test issue",
            body="Issue body",
            state="open",
            user=user,
            assignee=None,
            assignees=[],
            labels=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            closed_at=None,
            html_url="https://github.com/testuser/repo/issues/1",
        )

        # Test user table output
        with patch("mygh.utils.formatting.format_user_info") as mock_format:
            print_output(user, "table")
            mock_format.assert_called_once()

        # Test repo table output
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([repo], "table")
            mock_console.print.assert_called_once()

        # Test starred repo table output
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([repo], "table", is_starred=True)
            mock_console.print.assert_called_once()

        # Test gist table output
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([gist], "table")
            mock_console.print.assert_called_once()

        # Test issue table output
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([issue], "table")
            mock_console.print.assert_called_once()

        # Test user list table output
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([user], "table")
            mock_console.print.assert_called_once()

        # Test CSV output for repos
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([repo], "csv")
            mock_console.print.assert_called_once()

        # Test CSV output for starred repos
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([repo], "csv", is_starred=True)
            mock_console.print.assert_called_once()

        # Test JSON output
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([repo], "json")
            mock_console.print.assert_called_once()

        # Test file output
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
            tmp_path = tmp.name

        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([repo], "csv", tmp_path)
            mock_console.print.assert_called_once()

        # Test table format to file warning
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output([repo], "table", "output.txt")
            call_args = mock_console.print.call_args[0][0]
            assert "Table format cannot be saved to file" in call_args

    def test_commit_age_edge_cases(self):
        """Test commit age calculations with edge cases."""

        with patch("mygh.utils.formatting.datetime") as mock_dt:
            # Mock current time
            mock_now = datetime(2023, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
            mock_dt.now.return_value = mock_now
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Test various time differences
            test_cases = [
                # Same day
                (datetime(2023, 6, 22, 10, 0, 0, tzinfo=timezone.utc), "Today"),
                # 1 day ago
                (datetime(2023, 6, 21, 10, 0, 0, tzinfo=timezone.utc), "1 day"),
                # 1 week ago
                (datetime(2023, 6, 15, 10, 0, 0, tzinfo=timezone.utc), "7 days"),
                # 1 month ago
                (datetime(2023, 5, 22, 10, 0, 0, tzinfo=timezone.utc), "31 days"),
                # 1 year ago
                (datetime(2022, 6, 22, 10, 0, 0, tzinfo=timezone.utc), "365 days"),
            ]

            for pushed_at, expected in test_cases:
                result = calculate_days_since_commit(pushed_at)
                assert result == expected

                # Test styling too
                style_result = get_commit_age_style(pushed_at)
                assert str(style_result) == expected

    def test_formatting_with_unknown_list_type(self):
        """Test formatting with unknown list type."""
        unknown_data = [{"unknown": "data"}]

        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(unknown_data, "table")
            # For unknown list types, it prints the data directly
            mock_console.print.assert_called_with(unknown_data)
