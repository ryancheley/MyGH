"""Pytest configuration and fixtures."""

import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from mygh.api.models import GitHubRepo, GitHubUser


def strip_ansi_codes(text: str) -> str:
    """Strip ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


@pytest.fixture
def cli_runner():
    """CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_github_token():
    """Mock GitHub token."""
    with patch.dict(os.environ, {"GITHUB_TOKEN": "test_token_123"}):
        yield "test_token_123"


@pytest.fixture
def temp_config_dir():
    """Temporary configuration directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_dir = Path(temp_dir) / ".config" / "mygh"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Patch the Path.home() method used in ConfigManager.__init__
        with patch("mygh.utils.config.Path.home") as mock_home:
            mock_home.return_value = Path(temp_dir)
            yield config_dir


@pytest.fixture
def sample_user_data() -> dict[str, Any]:
    """Sample GitHub user data."""
    return {
        "id": 12345,
        "login": "testuser",
        "name": "Test User",
        "email": "test@example.com",
        "bio": "A test user",
        "company": "Test Corp",
        "location": "Test City",
        "blog": "https://test.example.com",
        "public_repos": 50,
        "public_gists": 10,
        "followers": 100,
        "following": 75,
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "avatar_url": "https://avatars.example.com/testuser",
        "html_url": "https://github.com/testuser",
    }


@pytest.fixture
def sample_repo_data() -> dict[str, Any]:
    """Sample GitHub repository data."""
    return {
        "id": 67890,
        "name": "test-repo",
        "full_name": "testuser/test-repo",
        "description": "A test repository",
        "private": False,
        "fork": False,
        "language": "Python",
        "stargazers_count": 42,
        "watchers_count": 35,
        "forks_count": 8,
        "open_issues_count": 3,
        "size": 1024,
        "default_branch": "main",
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2023-06-01T12:00:00Z",
        "pushed_at": "2023-06-20T15:30:00Z",
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


@pytest.fixture
def sample_gist_data() -> dict[str, Any]:
    """Sample GitHub gist data."""
    return {
        "id": "abc123",
        "description": "Test gist",
        "public": True,
        "created_at": "2022-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "html_url": "https://gist.github.com/testuser/abc123",
        "files": {
            "test.py": {
                "filename": "test.py",
                "type": "text/plain",
                "language": "Python",
                "raw_url": "https://gist.githubusercontent.com/testuser/abc123/raw/test.py",
                "size": 100,
            }
        },
        "owner": {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "https://avatars.example.com/testuser",
            "html_url": "https://github.com/testuser",
        },
    }


@pytest.fixture
def sample_issue_data() -> dict[str, Any]:
    """Sample GitHub issue data."""
    return {
        "id": 11111,
        "number": 1,
        "title": "Test issue",
        "body": "This is a test issue",
        "state": "open",
        "user": {
            "id": 12345,
            "login": "testuser",
            "avatar_url": "https://avatars.example.com/testuser",
            "html_url": "https://github.com/testuser",
        },
        "assignee": None,
        "assignees": [],
        "labels": [
            {"name": "bug", "color": "d73a4a"},
            {"name": "help wanted", "color": "008672"},
        ],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "closed_at": None,
        "html_url": "https://github.com/testuser/test-repo/issues/1",
    }


@pytest.fixture
def sample_user() -> GitHubUser:
    """Sample GitHubUser instance."""
    return GitHubUser(
        id=12345,
        login="testuser",
        name="Test User",
        email="test@example.com",
        bio="A test user",
        company="Test Corp",
        location="Test City",
        blog="https://test.example.com",
        public_repos=50,
        public_gists=10,
        followers=100,
        following=75,
        created_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        avatar_url="https://avatars.example.com/testuser",
        html_url="https://github.com/testuser",
    )


@pytest.fixture
def sample_repo(sample_user) -> GitHubRepo:
    """Sample GitHubRepo instance."""
    return GitHubRepo(
        id=67890,
        name="test-repo",
        full_name="testuser/test-repo",
        description="A test repository",
        private=False,
        fork=False,
        language="Python",
        stargazers_count=42,
        watchers_count=35,
        forks_count=8,
        open_issues_count=3,
        size=1024,
        default_branch="main",
        created_at=datetime(2021, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 6, 1, 12, 0, tzinfo=timezone.utc),
        pushed_at=datetime(2023, 6, 20, 15, 30, tzinfo=timezone.utc),
        html_url="https://github.com/testuser/test-repo",
        clone_url="https://github.com/testuser/test-repo.git",
        ssh_url="git@github.com:testuser/test-repo.git",
        owner=sample_user,
    )


@pytest.fixture
def frozen_time():
    """Freeze time to a specific datetime for consistent testing."""
    frozen_dt = datetime(2023, 6, 22, 12, 0, 0, tzinfo=timezone.utc)
    with patch("mygh.utils.formatting.datetime") as mock_dt:
        mock_dt.now.return_value = frozen_dt
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield frozen_dt
