"""Extended tests for formatting utilities to improve coverage."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from rich.table import Table
from rich.text import Text

from mygh.api.models import (
    GitHubBranch,
    GitHubPullRequest,
    GitHubRepo,
    GitHubUser,
)
from mygh.utils.formatting import (
    format_date,
    format_json,
    format_pull_request_table,
    format_repo_table,
    format_size,
    format_starred_repo_table,
    get_commit_age_style,
    print_output,
)


class TestUtilityFormatting:
    """Test utility formatting functions."""

    def test_format_date(self):
        """Test date formatting function."""
        dt = datetime(2023, 6, 22, 15, 30, 45, tzinfo=timezone.utc)
        result = format_date(dt)
        assert result == "2023-06-22"

    def test_format_size_bytes(self):
        """Test format_size for bytes."""
        result = format_size(512)
        assert result == "512B"

    def test_format_size_kilobytes(self):
        """Test format_size for kilobytes."""
        result = format_size(1536)  # 1.5 KB
        assert result == "1.5KB"

    def test_format_size_megabytes(self):
        """Test format_size for megabytes."""
        result = format_size(1572864)  # 1.5 MB
        assert result == "1.5MB"

    def test_format_size_gigabytes(self):
        """Test format_size for gigabytes."""
        result = format_size(1610612736)  # 1.5 GB
        assert result == "1.5GB"

    def test_format_size_edge_cases(self):
        """Test format_size edge cases."""
        assert format_size(1023) == "1023B"
        assert format_size(1024) == "1.0KB"
        assert format_size(1048575) == "1024.0KB"
        assert format_size(1048576) == "1.0MB"

    def test_get_commit_age_style_naive_datetime(self):
        """Test get_commit_age_style with naive datetime (line 73)."""
        from unittest.mock import patch

        # Create a naive datetime (no timezone info)
        naive_dt = datetime(2023, 6, 20, 10, 0, 0)  # No timezone

        # Mock the current time
        with patch("mygh.utils.formatting.datetime") as mock_datetime:
            mock_now = datetime(2023, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.timezone = timezone  # Ensure timezone is available

            result = get_commit_age_style(naive_dt)
            assert isinstance(result, Text)
            # The naive datetime should be treated as UTC, so 2 days difference
            assert "2 days" in str(result)


class TestTableFormatting:
    """Test table formatting functions."""

    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return GitHubUser(
            id=1,
            login="testuser",
            name="Test User",
            avatar_url="https://github.com/images/error/testuser.gif",
            html_url="https://github.com/testuser",
        )

    @pytest.fixture
    def sample_repo_for_starred(self, sample_user):
        """Create a sample repo for starred table testing."""
        return GitHubRepo(
            id=1,
            node_id="test-node",
            name="test-repo",
            full_name="testuser/test-repo",
            private=False,
            owner=sample_user,
            html_url="https://github.com/testuser/test-repo",
            description=("A test repository with a very long description that should be truncated"),
            fork=False,
            url="https://api.github.com/repos/testuser/test-repo",
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            pushed_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            size=100,
            stargazers_count=5,
            watchers_count=3,
            language="Python",
            has_issues=True,
            has_projects=True,
            has_wiki=True,
            has_pages=False,
            has_downloads=True,
            archived=False,
            disabled=False,
            open_issues_count=2,
            license=None,
            forks_count=1,
            open_issues=2,
            watchers=3,
            default_branch="main",
        )

    @pytest.fixture
    def sample_repo_long_url(self, sample_user):
        """Create a sample repo with a very long URL."""
        return GitHubRepo(
            id=1,
            node_id="test-node",
            name="test-repo",
            full_name="testuser/test-repo",
            private=False,
            owner=sample_user,
            html_url="https://github.com/testuser/very-long-repository-name-that-exceeds-limits",
            description="Short description",
            fork=False,
            url="https://api.github.com/repos/testuser/test-repo",
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            pushed_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            size=100,
            stargazers_count=5,
            watchers_count=3,
            language="Python",
            has_issues=True,
            has_projects=True,
            has_wiki=True,
            has_pages=False,
            has_downloads=True,
            archived=False,
            disabled=False,
            open_issues_count=2,
            license=None,
            forks_count=1,
            open_issues=2,
            watchers=3,
            default_branch="main",
        )

    @pytest.fixture
    def sample_pull_request(self, sample_user, sample_repo_for_starred):
        """Create a sample pull request."""
        return GitHubPullRequest(
            id=1,
            number=1,
            title=("Add feature that has a very long title that should be truncated for display"),
            user=sample_user,
            state="open",
            head=GitHubBranch(
                label="testuser:feature-branch",
                ref="feature-branch",
                sha="abc123",
                user=sample_user,
                repo=sample_repo_for_starred,
            ),
            base=GitHubBranch(
                label="testuser:main",
                ref="main",
                sha="def456",
                user=sample_user,
                repo=sample_repo_for_starred,
            ),
            created_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            html_url="https://github.com/testuser/test-repo/pull/1",
            diff_url="https://github.com/testuser/test-repo/pull/1.diff",
            patch_url="https://github.com/testuser/test-repo/pull/1.patch",
        )

    def test_format_starred_repo_table_description_truncation(self, sample_repo_for_starred):
        """Test starred repo table with description truncation."""
        repos = [sample_repo_for_starred]
        table = format_starred_repo_table(repos)

        assert isinstance(table, Table)
        assert table.title == "Starred GitHub Repositories"

    def test_format_starred_repo_table_url_truncation(self, sample_repo_long_url):
        """Test starred repo table with URL truncation."""
        repos = [sample_repo_long_url]
        table = format_starred_repo_table(repos)

        assert isinstance(table, Table)
        assert table.title == "Starred GitHub Repositories"

    def test_format_pull_request_table(self, sample_pull_request):
        """Test pull request table formatting."""
        pulls = [sample_pull_request]
        table = format_pull_request_table(pulls)

        assert isinstance(table, Table)
        assert table.title == "GitHub Pull Requests"

    def test_format_pull_request_table_closed_state(self, sample_pull_request, sample_user, sample_repo_for_starred):
        """Test pull request table with closed state."""
        closed_pr = GitHubPullRequest(
            id=2,
            number=2,
            title="Closed PR",
            user=sample_user,
            state="closed",
            head=GitHubBranch(
                label="testuser:feature-branch",
                ref="feature-branch",
                sha="abc123",
                user=sample_user,
                repo=sample_repo_for_starred,
            ),
            base=GitHubBranch(
                label="testuser:main",
                ref="main",
                sha="def456",
                user=sample_user,
                repo=sample_repo_for_starred,
            ),
            created_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            html_url="https://github.com/testuser/test-repo/pull/2",
            diff_url="https://github.com/testuser/test-repo/pull/2.diff",
            patch_url="https://github.com/testuser/test-repo/pull/2.patch",
        )

        pulls = [closed_pr]
        table = format_pull_request_table(pulls)

        assert isinstance(table, Table)

    def test_format_repo_table_description_truncation(self, sample_user):
        """Test repo table with description truncation (line 128)."""
        long_desc_repo = GitHubRepo(
            id=1,
            node_id="test-node",
            name="test-repo",
            full_name="testuser/test-repo",
            private=False,
            owner=sample_user,
            html_url="https://github.com/testuser/test-repo",
            description=(
                "This is a very long description that definitely exceeds 47 characters and should be truncated"
            ),
            fork=False,
            url="https://api.github.com/repos/testuser/test-repo",
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            pushed_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            size=100,
            stargazers_count=5,
            watchers_count=3,
            language="Python",
            has_issues=True,
            has_projects=True,
            has_wiki=True,
            has_pages=False,
            has_downloads=True,
            archived=False,
            disabled=False,
            open_issues_count=2,
            license=None,
            forks_count=1,
            open_issues=2,
            watchers=3,
            default_branch="main",
        )

        repos = [long_desc_repo]
        table = format_repo_table(repos)
        assert isinstance(table, Table)
        assert table.title == "GitHub Repositories"


class TestJsonFormatting:
    """Test JSON formatting functions."""

    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return GitHubUser(
            id=1,
            login="testuser",
            name="Test User",
            avatar_url="https://github.com/images/error/testuser.gif",
            html_url="https://github.com/testuser",
        )

    def test_format_json_with_model_dump(self, sample_user):
        """Test JSON formatting with model_dump."""
        result = format_json(sample_user)
        assert '"login": "testuser"' in result
        assert '"name": "Test User"' in result

    def test_format_json_with_list_model_dump(self, sample_user):
        """Test JSON formatting with list of models."""
        users = [sample_user]
        result = format_json(users)
        assert '"login": "testuser"' in result

    def test_format_json_with_dict_fallback(self):
        """Test JSON formatting with dict fallback for older pydantic."""

        # Mock an object with dict method instead of model_dump
        class OldPydanticModel:
            def dict(self):
                return {"old_field": "old_value"}

        obj = OldPydanticModel()
        result = format_json(obj)
        assert '"old_field": "old_value"' in result

    def test_format_json_with_list_dict_fallback(self):
        """Test JSON formatting with list dict fallback."""

        class OldPydanticModel:
            def dict(self):
                return {"old_field": "old_value"}

        objs = [OldPydanticModel()]
        result = format_json(objs)
        assert '"old_field": "old_value"' in result

    def test_format_json_with_regular_dict(self):
        """Test JSON formatting with regular dictionary."""
        data = {"key": "value", "number": 42}
        result = format_json(data)
        assert '"key": "value"' in result
        assert '"number": 42' in result


class TestPrintOutputExtended:
    """Test extended print_output functionality."""

    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return GitHubUser(
            id=1,
            login="testuser",
            name="Test User",
            avatar_url="https://github.com/images/error/testuser.gif",
            html_url="https://github.com/testuser",
        )

    @pytest.fixture
    def sample_pull_request(self, sample_user):
        """Create a sample pull request."""
        # Create a minimal repo for the PR
        sample_repo = GitHubRepo(
            id=1,
            node_id="test-node",
            name="test-repo",
            full_name="testuser/test-repo",
            private=False,
            owner=sample_user,
            html_url="https://github.com/testuser/test-repo",
            description="Test repo",
            fork=False,
            url="https://api.github.com/repos/testuser/test-repo",
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            pushed_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            clone_url="https://github.com/testuser/test-repo.git",
            ssh_url="git@github.com:testuser/test-repo.git",
            size=100,
            stargazers_count=5,
            watchers_count=3,
            language="Python",
            has_issues=True,
            has_projects=True,
            has_wiki=True,
            has_pages=False,
            has_downloads=True,
            archived=False,
            disabled=False,
            open_issues_count=2,
            license=None,
            forks_count=1,
            open_issues=2,
            watchers=3,
            default_branch="main",
        )

        return GitHubPullRequest(
            id=1,
            number=1,
            title="Test PR",
            user=sample_user,
            state="open",
            head=GitHubBranch(
                label="testuser:feature-branch",
                ref="feature-branch",
                sha="abc123",
                user=sample_user,
                repo=sample_repo,
            ),
            base=GitHubBranch(
                label="testuser:main",
                ref="main",
                sha="def456",
                user=sample_user,
                repo=sample_repo,
            ),
            created_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
            html_url="https://github.com/testuser/test-repo/pull/1",
            diff_url="https://github.com/testuser/test-repo/pull/1.diff",
            patch_url="https://github.com/testuser/test-repo/pull/1.patch",
        )

    def test_print_output_pull_requests(self, sample_pull_request):
        """Test print_output with pull requests."""
        prs = [sample_pull_request]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(prs, "table")
            mock_console.print.assert_called_once()

    def test_print_output_users(self, sample_user):
        """Test print_output with users."""
        users = [sample_user]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(users, "table")
            mock_console.print.assert_called_once()

    def test_print_output_unknown_type(self):
        """Test print_output with unknown data type."""
        unknown_data = [{"unknown": "data"}]
        with patch("mygh.utils.formatting.console") as mock_console:
            print_output(unknown_data, "table")
            mock_console.print.assert_called_once()
