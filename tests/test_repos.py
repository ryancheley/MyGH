"""Tests for the repos CLI commands."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from typer.testing import CliRunner

from mygh.api.models import GitHubIssue, GitHubRepo, GitHubUser
from mygh.cli.main import app
from mygh.exceptions import APIError, AuthenticationError, MyGHException


class TestReposCommands:
    """Test the repos CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_user(self):
        """Create a mock GitHub user."""
        return GitHubUser(
            login="testuser",
            id=1,
            node_id="MDQ6VXNlcjE=",
            avatar_url="https://github.com/images/error/testuser_happy.gif",
            gravatar_id="",
            url="https://api.github.com/users/testuser",
            html_url="https://github.com/testuser",
            followers_url="https://api.github.com/users/testuser/followers",
            following_url="https://api.github.com/users/testuser/following{/other_user}",
            gists_url="https://api.github.com/users/testuser/gists{/gist_id}",
            starred_url="https://api.github.com/users/testuser/starred{/owner}{/repo}",
            subscriptions_url="https://api.github.com/users/testuser/subscriptions",
            organizations_url="https://api.github.com/users/testuser/orgs",
            repos_url="https://api.github.com/users/testuser/repos",
            events_url="https://api.github.com/users/testuser/events{/privacy}",
            received_events_url="https://api.github.com/users/testuser/received_events",
            type="User",
            site_admin=False,
        )

    @pytest.fixture
    def mock_repo(self, mock_user):
        """Create a mock GitHub repository."""
        return GitHubRepo(
            id=1,
            node_id="MDEwOlJlcG9zaXRvcnkx",
            name="test-repo",
            full_name="testuser/test-repo",
            private=False,
            owner=mock_user,
            html_url="https://github.com/testuser/test-repo",
            description="A test repository",
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
            topics=["python", "testing"],
        )

    @pytest.fixture
    def mock_issue(self, mock_user):
        """Create a mock GitHub issue."""
        return GitHubIssue(
            id=1,
            node_id="MDU6SXNzdWUx",
            number=1,
            title="Test Issue",
            user=mock_user,
            labels=[],
            state="open",
            locked=False,
            assignee=None,
            assignees=[],
            milestone=None,
            comments=0,
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            closed_at=None,
            author_association="OWNER",
            body="Test issue body",
            html_url="https://github.com/testuser/test-repo/issues/1",
            url="https://api.github.com/repos/testuser/test-repo/issues/1",
        )

    def test_repos_list_help(self, runner):
        """Test repos list command help."""
        result = runner.invoke(app, ["repos", "list", "--help"])
        assert result.exit_code == 0
        assert "List repositories" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_list_basic(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test basic repository listing."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(return_value=[mock_repo])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 0
        mock_client.get_user_repos.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_list_with_username(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test repository listing with username."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(return_value=[mock_repo])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list", "testuser"])

        assert result.exit_code == 0
        mock_client.get_user_repos.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_list_with_options(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test repository listing with various options."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(return_value=[mock_repo])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "repos",
                "list",
                "testuser",
                "--type",
                "public",
                "--sort",
                "created",
                "--limit",
                "10",
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        mock_client.get_user_repos.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_list_empty_result(self, mock_client_class, mock_config_manager, runner):
        """Test repository listing with empty result."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(return_value=[])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 0
        assert "No repositories found" in result.stdout
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_list_pagination(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test repository listing with pagination."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        # Simulate pagination - first call returns 100 repos, second returns fewer
        mock_client.get_user_repos = AsyncMock(
            side_effect=[
                [mock_repo] * 100,  # First page
                [mock_repo] * 50,  # Second page (less than per_page)
            ]
        )
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list", "--limit", "150"])

        assert result.exit_code == 0
        assert mock_client.get_user_repos.call_count == 2
        mock_client.close.assert_called_once()

    def test_repos_info_help(self, runner):
        """Test repos info command help."""
        result = runner.invoke(app, ["repos", "info", "--help"])
        assert result.exit_code == 0
        assert "Get repository information" in result.stdout

    def test_repos_info_invalid_format(self, runner):
        """Test repos info with invalid repository format."""
        result = runner.invoke(app, ["repos", "info", "invalid-repo-name"])
        assert result.exit_code == 1
        assert "Repository name must be in 'owner/repo' format" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_info_basic(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test basic repository info."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(return_value=[mock_repo])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "info", "testuser/test-repo"])

        assert result.exit_code == 0
        mock_client.get_user_repos.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_info_not_found(self, mock_client_class, mock_config_manager, runner):
        """Test repository info when repo not found."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        # Empty list = not found
        mock_client.get_user_repos = AsyncMock(return_value=[])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "info", "testuser/nonexistent-repo"])

        assert result.exit_code == 1
        assert "Repository 'testuser/nonexistent-repo' not found" in result.stdout
        mock_client.close.assert_called_once()

    def test_repos_issues_help(self, runner):
        """Test repos issues command help."""
        result = runner.invoke(app, ["repos", "issues", "--help"])
        assert result.exit_code == 0
        assert "List repository issues" in result.stdout

    def test_repos_issues_invalid_format(self, runner):
        """Test repos issues with invalid repository format."""
        result = runner.invoke(app, ["repos", "issues", "invalid-repo-name"])
        assert result.exit_code == 1
        assert "Repository name must be in 'owner/repo' format" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_issues_basic(self, mock_client_class, mock_config_manager, runner, mock_issue):
        """Test basic repository issues listing."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_repo_issues = AsyncMock(return_value=[mock_issue])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "issues", "testuser/test-repo"])

        assert result.exit_code == 0
        mock_client.get_repo_issues.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_issues_with_options(self, mock_client_class, mock_config_manager, runner, mock_issue):
        """Test repository issues with various options."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_repo_issues = AsyncMock(return_value=[mock_issue])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(
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
                "bug,enhancement",
                "--limit",
                "50",
                "--format",
                "json",
            ],
        )

        assert result.exit_code == 0
        mock_client.get_repo_issues.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_issues_empty_result(self, mock_client_class, mock_config_manager, runner):
        """Test repository issues with empty result."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_repo_issues = AsyncMock(return_value=[])
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "issues", "testuser/test-repo"])

        assert result.exit_code == 0
        assert "No issues found" in result.stdout
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_issues_pagination(self, mock_client_class, mock_config_manager, runner, mock_issue):
        """Test repository issues with pagination."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        # Simulate pagination
        mock_client.get_repo_issues = AsyncMock(
            side_effect=[
                [mock_issue] * 100,  # First page
                [mock_issue] * 30,  # Second page (less than per_page)
            ]
        )
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "issues", "testuser/test-repo", "--limit", "130"])

        assert result.exit_code == 0
        assert mock_client.get_repo_issues.call_count == 2
        mock_client.close.assert_called_once()

    def test_repos_create_help(self, runner):
        """Test repos create command help."""
        result = runner.invoke(app, ["repos", "create", "--help"])
        assert result.exit_code == 0
        assert "Create a new repository" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_create_basic(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test basic repository creation."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.create_repo = AsyncMock(return_value=mock_repo)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "create", "new-repo"])

        assert result.exit_code == 0
        assert "Repository 'testuser/test-repo' created successfully!" in result.stdout
        mock_client.create_repo.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_create_with_options(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test repository creation with various options."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.create_repo = AsyncMock(return_value=mock_repo)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "repos",
                "create",
                "new-repo",
                "--description",
                "A new repository",
                "--private",
                "--no-issues",
                "--no-wiki",
                "--gitignore",
                "Python",
                "--license",
                "MIT",
            ],
        )

        assert result.exit_code == 0
        mock_client.create_repo.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.Prompt.ask")
    @patch("mygh.cli.repos.Confirm.ask")
    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_create_interactive(
        self,
        mock_client_class,
        mock_config_manager,
        mock_confirm,
        mock_prompt,
        runner,
        mock_repo,
    ):
        """Test interactive repository creation."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.create_repo = AsyncMock(return_value=mock_repo)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        # Mock interactive prompts
        mock_prompt.side_effect = ["new-repo", "A new repo", "", ""]
        # private, issues, wiki, projects, auto_init
        mock_confirm.side_effect = [False, True, True, True, True]

        result = runner.invoke(app, ["repos", "create", "initial-name", "--interactive"])

        assert result.exit_code == 0
        mock_client.create_repo.assert_called_once()
        mock_client.close.assert_called_once()

    def test_repos_update_help(self, runner):
        """Test repos update command help."""
        result = runner.invoke(app, ["repos", "update", "--help"])
        assert result.exit_code == 0
        assert "Update repository settings" in result.stdout

    def test_repos_update_invalid_format(self, runner):
        """Test repos update with invalid repository format."""
        result = runner.invoke(app, ["repos", "update", "invalid-repo-name"])
        assert result.exit_code == 1
        assert "Repository name must be in 'owner/repo' format" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_update_no_changes(self, mock_client_class, mock_config_manager, runner):
        """Test repository update with no changes specified."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "update", "testuser/test-repo"])

        assert result.exit_code == 0
        assert "No updates specified" in result.stdout
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_update_basic(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test basic repository update."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.update_repo = AsyncMock(return_value=mock_repo)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "repos",
                "update",
                "testuser/test-repo",
                "--description",
                "Updated description",
            ],
        )

        assert result.exit_code == 0
        assert "Repository 'testuser/test-repo' updated successfully!" in result.stdout
        mock_client.update_repo.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_update_all_options(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test repository update with all options."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.update_repo = AsyncMock(return_value=mock_repo)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "repos",
                "update",
                "testuser/test-repo",
                "--description",
                "Updated description",
                "--homepage",
                "https://example.com",
                "--private",
                "--no-issues",
                "--no-wiki",
                "--no-projects",
                "--no-squash",
                "--no-merge",
                "--no-rebase",
                "--keep-branch",
                "--archive",
            ],
        )

        assert result.exit_code == 0
        mock_client.update_repo.assert_called_once()
        mock_client.close.assert_called_once()

    def test_repos_delete_help(self, runner):
        """Test repos delete command help."""
        result = runner.invoke(app, ["repos", "delete", "--help"])
        assert result.exit_code == 0
        assert "Delete a repository" in result.stdout

    def test_repos_delete_invalid_format(self, runner):
        """Test repos delete with invalid repository format."""
        result = runner.invoke(app, ["repos", "delete", "invalid-repo-name"])
        assert result.exit_code == 1
        assert "Repository name must be in 'owner/repo' format" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_delete_force(self, mock_client_class, mock_config_manager, runner):
        """Test repository deletion with force flag."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.delete_repo = AsyncMock()
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "delete", "testuser/test-repo", "--force"])

        assert result.exit_code == 0
        assert "Repository 'testuser/test-repo' deleted successfully" in result.stdout
        mock_client.delete_repo.assert_called_once_with("testuser", "test-repo")
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.Prompt.ask")
    @patch("mygh.cli.repos.Confirm.ask")
    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_delete_with_confirmation(
        self,
        mock_client_class,
        mock_config_manager,
        mock_confirm,
        mock_prompt,
        runner,
    ):
        """Test repository deletion with confirmation."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.delete_repo = AsyncMock()
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        # Mock confirmation prompts
        mock_confirm.return_value = True
        mock_prompt.return_value = "testuser/test-repo"

        result = runner.invoke(app, ["repos", "delete", "testuser/test-repo"])

        assert result.exit_code == 0
        assert "Repository 'testuser/test-repo' deleted successfully" in result.stdout
        mock_client.delete_repo.assert_called_once_with("testuser", "test-repo")
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.Confirm.ask")
    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_delete_cancelled(self, mock_client_class, mock_config_manager, mock_confirm, runner):
        """Test repository deletion cancelled by user."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        # Mock confirmation prompts - user cancels
        mock_confirm.return_value = False

        result = runner.invoke(app, ["repos", "delete", "testuser/test-repo"])

        assert result.exit_code == 0
        assert "Repository deletion cancelled" in result.stdout
        # Note: client.close() is not called when user cancels before creating
        # client

    @patch("mygh.cli.repos.Prompt.ask")
    @patch("mygh.cli.repos.Confirm.ask")
    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_delete_wrong_confirmation(
        self,
        mock_client_class,
        mock_config_manager,
        mock_confirm,
        mock_prompt,
        runner,
    ):
        """Test repository deletion with wrong confirmation text."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        # Mock confirmation prompts
        mock_confirm.return_value = True
        mock_prompt.return_value = "wrong-repo-name"  # Wrong confirmation

        result = runner.invoke(app, ["repos", "delete", "testuser/test-repo"])

        assert result.exit_code == 0
        assert "Repository name doesn't match. Deletion cancelled." in result.stdout
        # Note: client.close() is not called when user provides wrong
        # confirmation

    def test_repos_fork_help(self, runner):
        """Test repos fork command help."""
        result = runner.invoke(app, ["repos", "fork", "--help"])
        assert result.exit_code == 0
        assert "Fork a repository" in result.stdout

    def test_repos_fork_invalid_format(self, runner):
        """Test repos fork with invalid repository format."""
        result = runner.invoke(app, ["repos", "fork", "invalid-repo-name"])
        assert result.exit_code == 1
        assert "Repository name must be in 'owner/repo' format" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_fork_basic(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test basic repository forking."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.fork_repo = AsyncMock(return_value=mock_repo)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "fork", "testuser/test-repo"])

        assert result.exit_code == 0
        assert "Repository 'testuser/test-repo' forked successfully!" in result.stdout
        mock_client.fork_repo.assert_called_once()
        mock_client.close.assert_called_once()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_repos_fork_to_organization(self, mock_client_class, mock_config_manager, runner, mock_repo):
        """Test repository forking to organization."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.fork_repo = AsyncMock(return_value=mock_repo)
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "fork", "testuser/test-repo", "--org", "myorg"])

        assert result.exit_code == 0
        mock_client.fork_repo.assert_called_once()
        mock_client.close.assert_called_once()


class TestReposExceptionHandling:
    """Test exception handling in repos commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_authentication_error_handling(self, mock_client_class, mock_config_manager, runner):
        """Test handling of authentication errors."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(side_effect=AuthenticationError("Invalid token"))
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 1
        assert "Authentication error" in result.stdout
        assert "To authenticate:" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_api_error_handling(self, mock_client_class, mock_config_manager, runner):
        """Test handling of API errors."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(side_effect=APIError("API rate limit exceeded"))
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 1
        assert "API error" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_mygh_exception_handling(self, mock_client_class, mock_config_manager, runner):
        """Test handling of MyGH exceptions."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(side_effect=MyGHException("Custom error"))
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 1
        assert "Error:" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_keyboard_interrupt_handling(self, mock_client_class, mock_config_manager, runner):
        """Test handling of keyboard interrupts."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(side_effect=KeyboardInterrupt())
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 0
        assert "Operation cancelled" in result.stdout

    @patch("mygh.cli.repos.config_manager")
    @patch("mygh.cli.repos.GitHubClient")
    @pytest.mark.api_mock
    def test_unexpected_exception_handling(self, mock_client_class, mock_config_manager, runner):
        """Test handling of unexpected exceptions."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config

        mock_client = AsyncMock()
        mock_client.get_user_repos = AsyncMock(side_effect=ValueError("Unexpected error"))
        mock_client.close = AsyncMock()
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["repos", "list"])

        assert result.exit_code == 1
        assert "Unexpected error" in result.stdout
