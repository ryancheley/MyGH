"""Tests for the browse CLI commands."""

import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from mygh.api.models import GitHubRepo, GitHubUser
from mygh.cli.browse import InteractiveBrowser
from mygh.cli.main import app


class TestInteractiveBrowser:
    """Test the InteractiveBrowser class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock GitHub client."""
        client = Mock()
        client.get_user_repos = Mock()
        return client

    @pytest.fixture
    def sample_repos(self):
        """Create sample repositories for testing."""
        user = GitHubUser(
            login="testowner",
            id=1,
            node_id="MDQ6VXNlcjE=",
            avatar_url="https://github.com/images/error/testowner_happy.gif",
            gravatar_id="",
            url="https://api.github.com/users/testowner",
            html_url="https://github.com/testowner",
            followers_url="https://api.github.com/users/testowner/followers",
            following_url="https://api.github.com/users/testowner/following{/other_user}",
            gists_url="https://api.github.com/users/testowner/gists{/gist_id}",
            starred_url="https://api.github.com/users/testowner/starred{/owner}{/repo}",
            subscriptions_url="https://api.github.com/users/testowner/subscriptions",
            organizations_url="https://api.github.com/users/testowner/orgs",
            repos_url="https://api.github.com/users/testowner/repos",
            events_url="https://api.github.com/users/testowner/events{/privacy}",
            received_events_url="https://api.github.com/users/testowner/received_events",
            type="User",
            site_admin=False,
        )

        return [
            GitHubRepo(
                id=1,
                node_id="MDEwOlJlcG9zaXRvcnkx",
                name="test-repo-1",
                full_name="testowner/test-repo-1",
                private=False,
                owner=user,
                html_url="https://github.com/testowner/test-repo-1",
                description="A test repository",
                fork=False,
                url="https://api.github.com/repos/testowner/test-repo-1",
                created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
                pushed_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
                clone_url="https://github.com/testowner/test-repo-1.git",
                ssh_url="git@github.com:testowner/test-repo-1.git",
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
            ),
            GitHubRepo(
                id=2,
                node_id="MDEwOlJlcG9zaXRvcnky",
                name="test-repo-2",
                full_name="testowner/test-repo-2",
                private=True,
                owner=user,
                html_url="https://github.com/testowner/test-repo-2",
                description="Another test repository with a very long description that should be truncated",
                fork=False,
                url="https://api.github.com/repos/testowner/test-repo-2",
                created_at=datetime(2023, 2, 1, tzinfo=timezone.utc),
                updated_at=datetime(2023, 5, 1, tzinfo=timezone.utc),
                pushed_at=datetime(2023, 5, 1, tzinfo=timezone.utc),
                clone_url="https://github.com/testowner/test-repo-2.git",
                ssh_url="git@github.com:testowner/test-repo-2.git",
                size=200,
                stargazers_count=10,
                watchers_count=5,
                language="JavaScript",
                has_issues=True,
                has_projects=True,
                has_wiki=True,
                has_pages=False,
                has_downloads=True,
                archived=False,
                disabled=False,
                open_issues_count=0,
                license=None,
                forks_count=3,
                open_issues=0,
                watchers=5,
                default_branch="main",
                topics=["javascript", "web"],
            ),
        ]

    def test_browser_initialization(self, mock_client):
        """Test browser initialization."""
        browser = InteractiveBrowser(mock_client)
        assert browser.client == mock_client
        assert browser.repositories == []
        assert browser.current_page == 0
        assert browser.per_page == 10
        assert browser.selected_index == 0
        assert browser.filter_text == ""

    @pytest.mark.asyncio
    async def test_load_repositories_success(self, mock_client, sample_repos):
        """Test successful repository loading."""
        mock_client.get_user_repos = asyncio.coroutine(Mock(return_value=sample_repos))
        
        browser = InteractiveBrowser(mock_client)
        result = await browser.load_repositories()
        
        assert result is True
        assert browser.repositories == sample_repos

    @pytest.mark.asyncio
    async def test_load_repositories_with_username(self, mock_client, sample_repos):
        """Test repository loading with username."""
        mock_client.get_user_repos.return_value = sample_repos
        
        browser = InteractiveBrowser(mock_client)
        result = await browser.load_repositories("testuser")
        
        assert result is True
        assert browser.repositories == sample_repos
        mock_client.get_user_repos.assert_called_once_with("testuser")

    @pytest.mark.asyncio
    async def test_load_repositories_error(self, mock_client):
        """Test repository loading with error."""
        from mygh.exceptions import APIError
        mock_client.get_user_repos.side_effect = APIError("API Error")
        
        browser = InteractiveBrowser(mock_client)
        result = await browser.load_repositories()
        
        assert result is False
        assert browser.repositories == []

    def test_get_filtered_repos_no_filter(self, mock_client, sample_repos):
        """Test filtering with no filter text."""
        browser = InteractiveBrowser(mock_client)
        browser.repositories = sample_repos
        
        filtered = browser.get_filtered_repos()
        assert filtered == sample_repos

    def test_get_filtered_repos_with_filter(self, mock_client, sample_repos):
        """Test filtering with filter text."""
        browser = InteractiveBrowser(mock_client)
        browser.repositories = sample_repos
        browser.filter_text = "python"
        
        filtered = browser.get_filtered_repos()
        assert len(filtered) == 1
        assert filtered[0].name == "test-repo-1"

    def test_get_filtered_repos_description_match(self, mock_client, sample_repos):
        """Test filtering by description."""
        browser = InteractiveBrowser(mock_client)
        browser.repositories = sample_repos
        browser.filter_text = "long description"
        
        filtered = browser.get_filtered_repos()
        assert len(filtered) == 1
        assert filtered[0].name == "test-repo-2"

    def test_get_current_page_repos(self, mock_client, sample_repos):
        """Test getting current page repositories."""
        browser = InteractiveBrowser(mock_client)
        browser.repositories = sample_repos
        browser.per_page = 1
        
        # First page
        repos, total = browser.get_current_page_repos()
        assert len(repos) == 1
        assert total == 2
        assert repos[0].name == "test-repo-1"
        
        # Second page
        browser.current_page = 1
        repos, total = browser.get_current_page_repos()
        assert len(repos) == 1
        assert total == 2
        assert repos[0].name == "test-repo-2"

    def test_get_current_page_repos_with_filter(self, mock_client, sample_repos):
        """Test getting current page with filter."""
        browser = InteractiveBrowser(mock_client)
        browser.repositories = sample_repos
        browser.filter_text = "python"
        
        repos, total = browser.get_current_page_repos()
        assert len(repos) == 1
        assert total == 1
        assert repos[0].name == "test-repo-1"

    @patch('mygh.cli.browse.console')
    def test_display_repositories_empty(self, mock_console, mock_client):
        """Test displaying empty repository list."""
        browser = InteractiveBrowser(mock_client)
        
        browser.display_repositories()
        
        mock_console.clear.assert_called_once()
        mock_console.print.assert_called()

    @patch('mygh.cli.browse.console')
    def test_display_repositories_with_data(self, mock_console, mock_client, sample_repos):
        """Test displaying repositories with data."""
        browser = InteractiveBrowser(mock_client)
        browser.repositories = sample_repos
        
        browser.display_repositories()
        
        mock_console.clear.assert_called_once()
        assert mock_console.print.call_count >= 3  # Panel, table, footer


class TestBrowseCLI:
    """Test the browse CLI commands."""

    def test_browse_help(self):
        """Test browse command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["browse", "--help"])
        assert result.exit_code == 0
        assert "Interactive repository browser" in result.stdout

    def test_browse_repos_help(self):
        """Test browse repos command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["browse", "repos", "--help"])
        assert result.exit_code == 0
        assert "Launch interactive repository browser" in result.stdout

    @patch('mygh.cli.browse.asyncio.run')
    @patch('mygh.cli.browse.get_config')
    @patch('mygh.cli.browse.GitHubClient')
    def test_browse_repos_command(self, mock_client_class, mock_get_config, mock_asyncio_run):
        """Test browse repos command execution."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client.__aenter__ = Mock(return_value=mock_client)
        mock_client.__aexit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(app, ["browse", "repos"])
        
        assert result.exit_code == 0
        mock_get_config.assert_called_once()
        mock_client_class.assert_called_once_with("fake_token")
        mock_asyncio_run.assert_called_once()

    @patch('mygh.cli.browse.asyncio.run')
    @patch('mygh.cli.browse.get_config')
    @patch('mygh.cli.browse.GitHubClient')
    def test_browse_repos_with_username(self, mock_client_class, mock_get_config, mock_asyncio_run):
        """Test browse repos command with username."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client.__aenter__ = Mock(return_value=mock_client)
        mock_client.__aexit__ = Mock(return_value=None)
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(app, ["browse", "repos", "testuser"])
        
        assert result.exit_code == 0
        mock_get_config.assert_called_once()
        mock_client_class.assert_called_once_with("fake_token")
        mock_asyncio_run.assert_called_once()

    @patch('mygh.cli.browse.console')
    @patch('mygh.cli.browse.asyncio.run')
    def test_browse_repos_keyboard_interrupt(self, mock_asyncio_run, mock_console):
        """Test browse repos command with keyboard interrupt."""
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        
        runner = CliRunner()
        result = runner.invoke(app, ["browse", "repos"])
        
        assert result.exit_code == 0
        mock_console.print.assert_called_with("\n[yellow]Browser closed.[/yellow]")


class TestRepoManagementCLI:
    """Test the repository management CLI commands."""

    def test_repos_create_help(self):
        """Test repos create command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "create", "--help"])
        assert result.exit_code == 0
        assert "Create a new repository" in result.stdout

    def test_repos_update_help(self):
        """Test repos update command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "update", "--help"])
        assert result.exit_code == 0
        assert "Update repository settings" in result.stdout

    def test_repos_delete_help(self):
        """Test repos delete command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "delete", "--help"])
        assert result.exit_code == 0
        assert "Delete a repository" in result.stdout

    def test_repos_fork_help(self):
        """Test repos fork command help."""
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "fork", "--help"])
        assert result.exit_code == 0
        assert "Fork a repository" in result.stdout

    @patch('mygh.cli.repos.GitHubClient')
    @patch('mygh.cli.repos.config_manager')
    def test_create_repo_basic(self, mock_config_manager, mock_client_class):
        """Test basic repository creation."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client.create_repo = Mock()
        mock_repo = Mock()
        mock_repo.full_name = "testowner/test-repo"
        mock_repo.html_url = "https://github.com/testowner/test-repo"
        mock_repo.clone_url = "https://github.com/testowner/test-repo.git"
        mock_client.create_repo.return_value = mock_repo
        mock_client.close = Mock()
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "create", "test-repo"])
        
        assert result.exit_code == 0
        mock_client.create_repo.assert_called_once()
        mock_client.close.assert_called_once()

    @patch('mygh.cli.repos.GitHubClient')
    @patch('mygh.cli.repos.config_manager')
    def test_update_repo_basic(self, mock_config_manager, mock_client_class):
        """Test basic repository update."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client.update_repo = Mock()
        mock_repo = Mock()
        mock_repo.full_name = "testowner/test-repo"
        mock_repo.html_url = "https://github.com/testowner/test-repo"
        mock_client.update_repo.return_value = mock_repo
        mock_client.close = Mock()
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "update", "testowner/test-repo", "--description", "New description"])
        
        assert result.exit_code == 0
        mock_client.update_repo.assert_called_once()
        mock_client.close.assert_called_once()

    @patch('mygh.cli.repos.Confirm.ask')
    @patch('mygh.cli.repos.Prompt.ask')
    @patch('mygh.cli.repos.GitHubClient')
    @patch('mygh.cli.repos.config_manager')
    def test_delete_repo_with_confirmation(self, mock_config_manager, mock_client_class, mock_prompt, mock_confirm):
        """Test repository deletion with confirmation."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client.delete_repo = Mock()
        mock_client.close = Mock()
        mock_client_class.return_value = mock_client
        
        mock_confirm.return_value = True
        mock_prompt.return_value = "testowner/test-repo"
        
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "delete", "testowner/test-repo"])
        
        assert result.exit_code == 0
        mock_client.delete_repo.assert_called_once_with("testowner", "test-repo")
        mock_client.close.assert_called_once()

    @patch('mygh.cli.repos.GitHubClient')
    @patch('mygh.cli.repos.config_manager')
    def test_fork_repo_basic(self, mock_config_manager, mock_client_class):
        """Test basic repository forking."""
        # Setup mocks
        mock_config = Mock()
        mock_config.github_token = "fake_token"
        mock_config_manager.get_config.return_value = mock_config
        
        mock_client = Mock()
        mock_client.fork_repo = Mock()
        mock_repo = Mock()
        mock_repo.html_url = "https://github.com/myuser/test-repo"
        mock_repo.clone_url = "https://github.com/myuser/test-repo.git"
        mock_client.fork_repo.return_value = mock_repo
        mock_client.close = Mock()
        mock_client_class.return_value = mock_client
        
        runner = CliRunner()
        result = runner.invoke(app, ["repos", "fork", "testowner/test-repo"])
        
        assert result.exit_code == 0
        mock_client.fork_repo.assert_called_once()
        mock_client.close.assert_called_once()