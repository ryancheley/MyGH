"""Tests for Pydantic models."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from mygh.api.models import GitHubGist, GitHubIssue, GitHubRepo, GitHubUser, RateLimit


class TestGitHubUser:
    """Test GitHubUser model."""

    def test_create_user_full_data(self, sample_user_data):
        """Test creating user with full data."""
        user = GitHubUser(**sample_user_data)

        assert user.id == 12345
        assert user.login == "testuser"
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.bio == "A test user"
        assert user.company == "Test Corp"
        assert user.location == "Test City"
        assert user.blog == "https://test.example.com"
        assert user.public_repos == 50
        assert user.public_gists == 10
        assert user.followers == 100
        assert user.following == 75
        assert user.avatar_url == "https://avatars.example.com/testuser"
        assert user.html_url == "https://github.com/testuser"

    def test_create_user_minimal_data(self):
        """Test creating user with minimal required data."""
        minimal_data = {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "https://avatars.example.com/testuser",
            "html_url": "https://github.com/testuser",
        }

        user = GitHubUser(**minimal_data)
        assert user.id == 12345
        assert user.login == "testuser"
        assert user.name is None
        assert user.public_repos is None
        assert user.followers is None

    def test_create_user_with_aliases(self):
        """Test creating user with field aliases."""
        data = {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "https://avatars.example.com/testuser",
            "html_url": "https://github.com/testuser",
            "public_repos": 50,
            "public_gists": 10,
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }

        user = GitHubUser(**data)
        assert user.public_repos == 50
        assert user.public_gists == 10
        assert user.created_at == datetime(2020, 1, 1, tzinfo=timezone.utc)

    def test_user_missing_required_field(self):
        """Test validation error with missing required field."""
        with pytest.raises(ValidationError) as exc_info:
            GitHubUser(login="testuser")  # Missing id

        assert "id" in str(exc_info.value)

    def test_user_invalid_field_type(self):
        """Test validation error with invalid field type."""
        with pytest.raises(ValidationError):
            GitHubUser(
                id="not_an_int",  # Should be int
                login="testuser",
                avatar_url="https://avatars.example.com/testuser",
                html_url="https://github.com/testuser",
            )


class TestGitHubRepo:
    """Test GitHubRepo model."""

    def test_create_repo_full_data(self, sample_repo_data):
        """Test creating repository with full data."""
        repo = GitHubRepo(**sample_repo_data)

        assert repo.id == 67890
        assert repo.name == "test-repo"
        assert repo.full_name == "testuser/test-repo"
        assert repo.description == "A test repository"
        assert repo.private is False
        assert repo.fork is False
        assert repo.language == "Python"
        assert repo.stargazers_count == 42
        assert repo.forks_count == 8
        assert repo.size == 1024
        assert repo.default_branch == "main"
        assert repo.html_url == "https://github.com/testuser/test-repo"

    def test_create_repo_with_null_description(self, sample_repo_data):
        """Test creating repository with null description."""
        sample_repo_data["description"] = None
        repo = GitHubRepo(**sample_repo_data)
        assert repo.description is None

    def test_create_repo_with_null_language(self, sample_repo_data):
        """Test creating repository with null language."""
        sample_repo_data["language"] = None
        repo = GitHubRepo(**sample_repo_data)
        assert repo.language is None

    def test_create_repo_with_null_pushed_at(self, sample_repo_data):
        """Test creating repository with null pushed_at."""
        sample_repo_data["pushed_at"] = None
        repo = GitHubRepo(**sample_repo_data)
        assert repo.pushed_at is None

    def test_repo_owner_relationship(self, sample_repo_data):
        """Test repository owner relationship."""
        repo = GitHubRepo(**sample_repo_data)
        assert isinstance(repo.owner, GitHubUser)
        assert repo.owner.login == "testuser"

    def test_repo_missing_required_field(self, sample_repo_data):
        """Test validation error with missing required field."""
        del sample_repo_data["name"]
        with pytest.raises(ValidationError) as exc_info:
            GitHubRepo(**sample_repo_data)

        assert "name" in str(exc_info.value)

    def test_repo_field_aliases(self, sample_repo_data):
        """Test repository field aliases work correctly."""
        repo = GitHubRepo(**sample_repo_data)
        assert repo.full_name == "testuser/test-repo"
        assert repo.stargazers_count == 42
        assert repo.watchers_count == 35


class TestGitHubGist:
    """Test GitHubGist model."""

    def test_create_gist_full_data(self, sample_gist_data):
        """Test creating gist with full data."""
        gist = GitHubGist(**sample_gist_data)

        assert gist.id == "abc123"
        assert gist.description == "Test gist"
        assert gist.public is True
        assert gist.html_url == "https://gist.github.com/testuser/abc123"
        assert "test.py" in gist.files

    def test_create_gist_with_null_description(self, sample_gist_data):
        """Test creating gist with null description."""
        sample_gist_data["description"] = None
        gist = GitHubGist(**sample_gist_data)
        assert gist.description is None

    def test_gist_owner_relationship(self, sample_gist_data):
        """Test gist owner relationship."""
        gist = GitHubGist(**sample_gist_data)
        assert isinstance(gist.owner, GitHubUser)
        assert gist.owner.login == "testuser"

    def test_gist_missing_required_field(self, sample_gist_data):
        """Test validation error with missing required field."""
        del sample_gist_data["id"]
        with pytest.raises(ValidationError):
            GitHubGist(**sample_gist_data)


class TestGitHubIssue:
    """Test GitHubIssue model."""

    def test_create_issue_full_data(self, sample_issue_data):
        """Test creating issue with full data."""
        issue = GitHubIssue(**sample_issue_data)

        assert issue.id == 11111
        assert issue.number == 1
        assert issue.title == "Test issue"
        assert issue.body == "This is a test issue"
        assert issue.state == "open"
        assert issue.html_url == "https://github.com/testuser/test-repo/issues/1"

    def test_create_issue_with_null_body(self, sample_issue_data):
        """Test creating issue with null body."""
        sample_issue_data["body"] = None
        issue = GitHubIssue(**sample_issue_data)
        assert issue.body is None

    def test_create_issue_with_null_assignee(self, sample_issue_data):
        """Test creating issue with null assignee."""
        sample_issue_data["assignee"] = None
        issue = GitHubIssue(**sample_issue_data)
        assert issue.assignee is None

    def test_create_issue_with_null_closed_at(self, sample_issue_data):
        """Test creating issue with null closed_at."""
        sample_issue_data["closed_at"] = None
        issue = GitHubIssue(**sample_issue_data)
        assert issue.closed_at is None

    def test_issue_user_relationship(self, sample_issue_data):
        """Test issue user relationship."""
        issue = GitHubIssue(**sample_issue_data)
        assert isinstance(issue.user, GitHubUser)
        assert issue.user.login == "testuser"

    def test_issue_labels_list(self, sample_issue_data):
        """Test issue labels list."""
        issue = GitHubIssue(**sample_issue_data)
        assert len(issue.labels) == 2
        assert issue.labels[0]["name"] == "bug"
        assert issue.labels[1]["name"] == "help wanted"

    def test_issue_assignees_list(self, sample_issue_data):
        """Test issue assignees list."""
        issue = GitHubIssue(**sample_issue_data)
        assert len(issue.assignees) == 0

    def test_issue_missing_required_field(self, sample_issue_data):
        """Test validation error with missing required field."""
        del sample_issue_data["title"]
        with pytest.raises(ValidationError):
            GitHubIssue(**sample_issue_data)


class TestRateLimit:
    """Test RateLimit model."""

    def test_create_rate_limit(self):
        """Test creating rate limit."""
        rate_limit = RateLimit(
            limit=5000,
            remaining=4999,
            reset=datetime(2023, 1, 1, tzinfo=timezone.utc),
            used=1,
        )

        assert rate_limit.limit == 5000
        assert rate_limit.remaining == 4999
        assert rate_limit.used == 1
        assert rate_limit.reset == datetime(2023, 1, 1, tzinfo=timezone.utc)

    def test_rate_limit_missing_required_field(self):
        """Test validation error with missing required field."""
        with pytest.raises(ValidationError):
            RateLimit(
                remaining=4999,
                reset=datetime(2023, 1, 1, tzinfo=timezone.utc),
                used=1,
            )  # Missing limit

    def test_rate_limit_invalid_field_type(self):
        """Test validation error with invalid field type."""
        with pytest.raises(ValidationError):
            RateLimit(
                limit="not_an_int",  # Should be int
                remaining=4999,
                reset=datetime(2023, 1, 1, tzinfo=timezone.utc),
                used=1,
            )


class TestModelIntegration:
    """Test model integration and edge cases."""

    def test_user_with_minimal_owner_data(self):
        """Test user model with minimal data as used in repository owner."""
        minimal_owner_data = {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "https://avatars.example.com/testuser",
            "html_url": "https://github.com/testuser",
        }

        user = GitHubUser(**minimal_owner_data)
        assert user.login == "testuser"
        assert user.public_repos is None
        assert user.followers is None

    def test_datetime_parsing(self):
        """Test datetime field parsing."""
        user_data = {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "https://avatars.example.com/testuser",
            "html_url": "https://github.com/testuser",
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2023-01-01T12:30:45Z",
        }

        user = GitHubUser(**user_data)
        assert user.created_at == datetime(2020, 1, 1, tzinfo=timezone.utc)
        assert user.updated_at == datetime(2023, 1, 1, 12, 30, 45, tzinfo=timezone.utc)

    def test_field_alias_consistency(self):
        """Test that field aliases work consistently."""
        repo_data = {
            "id": 67890,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "private": False,
            "fork": False,
            "size": 1024,
            "default_branch": "main",
            "stargazers_count": 42,  # Using alias
            "watchers_count": 35,  # Using alias
            "forks_count": 8,  # Using alias
            "open_issues_count": 3,  # Using alias
            "created_at": "2021-01-01T00:00:00Z",  # Using alias
            "updated_at": "2023-06-01T12:00:00Z",  # Using alias
            "html_url": "https://github.com/testuser/test-repo",
            "clone_url": "https://github.com/testuser/test-repo.git",
            "ssh_url": "git@github.com:testuser/test-repo.git",
            "owner": {
                "id": 12345,
                "login": "testuser",
                "avatar_url": "https://avatars.example.com/testuser",
                "html_url": "https://github.com/testuser",
            },
        }

        repo = GitHubRepo(**repo_data)
        assert repo.stargazers_count == 42
        assert repo.watchers_count == 35
        assert repo.forks_count == 8
