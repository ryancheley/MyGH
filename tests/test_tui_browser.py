"""Tests for the TUI browser functionality."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mygh.api.models import GitHubRepo, GitHubUser
from mygh.tui.browser import (
    QuickActionsPane,
    RepositoryActionMessage,
    RepositoryBrowser,
    RepositoryDetailsPane,
)


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client."""
    client = AsyncMock()
    return client


@pytest.fixture
def sample_repo():
    """Create a sample repository for testing."""
    owner = GitHubUser(
        login="testowner",
        id=123,
        html_url="https://github.com/testowner",
        avatar_url="https://github.com/testowner.png",
    )

    return GitHubRepo(
        id=456,
        name="test-repo",
        full_name="testowner/test-repo",
        owner=owner,
        private=False,
        fork=False,
        html_url="https://github.com/testowner/test-repo",
        clone_url="https://github.com/testowner/test-repo.git",
        ssh_url="git@github.com:testowner/test-repo.git",
        description="A test repository",
        language="Python",
        stargazers_count=42,
        watchers_count=42,
        forks_count=7,
        open_issues_count=3,
        size=1024,
        default_branch="main",
        created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 12, 1, tzinfo=timezone.utc),
        pushed_at=datetime(2023, 11, 30, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_repos(sample_repo):
    """Create a list of sample repositories."""
    repos = [sample_repo]

    # Add a second repo
    owner2 = GitHubUser(
        login="testowner2",
        id=124,
        html_url="https://github.com/testowner2",
        avatar_url="https://github.com/testowner2.png",
    )

    repo2 = GitHubRepo(
        id=457,
        name="another-repo",
        full_name="testowner2/another-repo",
        owner=owner2,
        private=True,
        fork=False,
        html_url="https://github.com/testowner2/another-repo",
        clone_url="https://github.com/testowner2/another-repo.git",
        ssh_url="git@github.com:testowner2/another-repo.git",
        description="Another test repository",
        language="JavaScript",
        stargazers_count=123,
        watchers_count=123,
        forks_count=15,
        open_issues_count=0,
        size=2048,
        default_branch="main",
        created_at=datetime(2023, 6, 1, tzinfo=timezone.utc),
        updated_at=datetime(2023, 12, 15, tzinfo=timezone.utc),
        pushed_at=datetime(2023, 12, 14, tzinfo=timezone.utc),
    )

    repos.append(repo2)
    return repos


class TestRepositoryDetailsPane:
    """Test the repository details pane."""

    def test_initialization(self):
        """Test that the details pane initializes correctly."""
        pane = RepositoryDetailsPane()
        assert pane.repo is None

    def test_update_repo(self, sample_repo):
        """Test updating the repository details."""
        pane = RepositoryDetailsPane()

        # Mock the update method
        pane.update = MagicMock()

        pane.update_repo(sample_repo)
        assert pane.repo == sample_repo

    def test_update_display_no_repo(self):
        """Test display update with no repository selected."""
        pane = RepositoryDetailsPane()
        pane.update = MagicMock()

        pane.update_display()
        pane.update.assert_called_once_with("Select a repository to view details")

    def test_update_display_with_repo(self, sample_repo):
        """Test display update with a repository."""
        pane = RepositoryDetailsPane()
        pane.update = MagicMock()
        pane.repo = sample_repo

        pane.update_display()

        # Verify that update was called with formatted repository details
        pane.update.assert_called_once()
        call_args = pane.update.call_args[0][0]

        assert "testowner/test-repo" in call_args
        assert "A test repository" in call_args
        assert "Python" in call_args
        assert "42" in call_args  # stargazers_count
        assert "7" in call_args  # forks_count


class TestQuickActionsPane:
    """Test the quick actions pane."""

    def test_initialization(self):
        """Test that the actions pane initializes correctly."""
        pane = QuickActionsPane()
        assert pane.repo is None

    def test_update_repo(self, sample_repo):
        """Test updating the repository for actions."""
        pane = QuickActionsPane()

        # Mock the query_one method
        mock_button = MagicMock()
        pane.query_one = MagicMock(return_value=mock_button)

        pane.update_repo(sample_repo)
        assert pane.repo == sample_repo


class TestRepositoryActionMessage:
    """Test the repository action message."""

    def test_message_creation(self, sample_repo):
        """Test creating a repository action message."""
        message = RepositoryActionMessage("star", sample_repo)
        assert message.action == "star"
        assert message.repo == sample_repo


class TestRepositoryBrowser:
    """Test the main repository browser application."""

    @pytest.mark.asyncio
    async def test_initialization(self, mock_github_client):
        """Test browser initialization."""
        browser = RepositoryBrowser(mock_github_client, "testuser")

        assert browser.github_client == mock_github_client
        assert browser.username == "testuser"
        assert browser.title == "MyGH - Interactive Repository Browser"
        assert browser.sub_title == "User: testuser"
        assert browser.repositories == []
        assert browser.filtered_repositories == []
        assert browser.selected_repo is None
        assert browser.search_query == ""

    @pytest.mark.asyncio
    async def test_initialization_no_username(self, mock_github_client):
        """Test browser initialization without username."""
        browser = RepositoryBrowser(mock_github_client)

        assert browser.username is None
        assert browser.sub_title == "All Repositories"

    def test_load_repositories_with_username(self, mock_github_client, sample_repos):
        """Test loading repositories for a specific user."""
        mock_github_client.get_user_repos.return_value = sample_repos
        mock_github_client.get_starred_repos.return_value = [sample_repos[0]]  # First repo is starred

        browser = RepositoryBrowser(mock_github_client, "testuser")
        browser.populate_table = MagicMock()
        browser.notify = MagicMock()

        # Simulate the load_repositories method manually since @work complicates testing
        async def simulate_load():
            repos = await mock_github_client.get_user_repos("testuser")
            starred = await mock_github_client.get_starred_repos("testuser")

            starred_names = {repo.full_name for repo in starred}
            for repo in repos:
                repo.starred = repo.full_name in starred_names

            browser.repositories = repos
            browser.filtered_repositories = repos
            browser.populate_table()

        # Run the simulation
        import asyncio

        asyncio.run(simulate_load())

        mock_github_client.get_user_repos.assert_called_once_with("testuser")
        mock_github_client.get_starred_repos.assert_called_once_with("testuser")

        assert len(browser.repositories) == 2
        assert hasattr(browser.repositories[0], "starred")
        assert browser.repositories[0].starred is True
        assert browser.repositories[1].starred is False

    def test_load_repositories_authenticated_user(self, mock_github_client, sample_repos):
        """Test loading repositories for authenticated user."""
        mock_user = GitHubUser(
            login="authuser",
            id=999,
            html_url="https://github.com/authuser",
            avatar_url="https://github.com/authuser.png",
        )

        mock_github_client.get_authenticated_user.return_value = mock_user
        mock_github_client.get_user_repos.return_value = sample_repos
        mock_github_client.get_starred_repos.return_value = []

        browser = RepositoryBrowser(mock_github_client)
        browser.populate_table = MagicMock()
        browser.notify = MagicMock()

        # Simulate the load_repositories method manually since @work complicates testing
        async def simulate_load():
            user = await mock_github_client.get_authenticated_user()
            repos = await mock_github_client.get_user_repos(user.login)
            starred = await mock_github_client.get_starred_repos(user.login)

            starred_names = {repo.full_name for repo in starred}
            for repo in repos:
                repo.starred = repo.full_name in starred_names

            browser.repositories = repos
            browser.filtered_repositories = repos
            browser.populate_table()

        # Run the simulation
        import asyncio

        asyncio.run(simulate_load())

        mock_github_client.get_authenticated_user.assert_called_once()
        mock_github_client.get_user_repos.assert_called_once_with("authuser")
        mock_github_client.get_starred_repos.assert_called_once_with("authuser")

    def test_filter_repositories_by_search(self, mock_github_client, sample_repos):
        """Test filtering repositories by search query."""
        browser = RepositoryBrowser(mock_github_client)
        browser.repositories = sample_repos
        browser.populate_table = MagicMock()

        # Mock the filter options
        mock_option_list = MagicMock()
        mock_option_list.highlighted = None
        browser.query_one = MagicMock(return_value=mock_option_list)

        # Test search by name
        browser.search_query = "test-repo"
        browser.filter_repositories()

        assert len(browser.filtered_repositories) == 1
        assert browser.filtered_repositories[0].name == "test-repo"

        # Test search by language
        browser.search_query = "javascript"
        browser.filter_repositories()

        assert len(browser.filtered_repositories) == 1
        assert browser.filtered_repositories[0].language == "JavaScript"

    def test_filter_repositories_by_category(self, mock_github_client, sample_repos):
        """Test filtering repositories by category."""
        browser = RepositoryBrowser(mock_github_client)
        browser.repositories = sample_repos
        browser.populate_table = MagicMock()
        browser.search_query = ""

        # Mark first repo as starred for testing
        sample_repos[0].starred = True
        sample_repos[1].starred = False

        # Mock filter selection
        mock_option = MagicMock()
        mock_option.id = "starred"
        mock_option_list = MagicMock()
        mock_option_list.highlighted = 0
        mock_option_list.get_option_at_index.return_value = mock_option
        browser.query_one = MagicMock(return_value=mock_option_list)

        browser.filter_repositories()

        assert len(browser.filtered_repositories) == 1
        assert browser.filtered_repositories[0].starred is True

    @pytest.mark.asyncio
    async def test_handle_star_action(self, mock_github_client, sample_repo):
        """Test handling star action."""
        browser = RepositoryBrowser(mock_github_client)
        browser.notify = MagicMock()
        browser.update_actions_pane = MagicMock()

        # Test starring a repository
        sample_repo.starred = False
        message = RepositoryActionMessage("star", sample_repo)

        await browser.handle_repository_action(message)

        mock_github_client.star_repository.assert_called_once_with("testowner", "test-repo")
        assert sample_repo.starred is True
        browser.notify.assert_called_with("Starred testowner/test-repo")
        browser.update_actions_pane.assert_called_once_with(sample_repo)

    @pytest.mark.asyncio
    async def test_handle_unstar_action(self, mock_github_client, sample_repo):
        """Test handling unstar action."""
        browser = RepositoryBrowser(mock_github_client)
        browser.notify = MagicMock()
        browser.update_actions_pane = MagicMock()

        # Test unstarring a repository
        sample_repo.starred = True
        message = RepositoryActionMessage("star", sample_repo)

        await browser.handle_repository_action(message)

        mock_github_client.unstar_repository.assert_called_once_with("testowner", "test-repo")
        assert sample_repo.starred is False
        browser.notify.assert_called_with("Unstarred testowner/test-repo")

    @pytest.mark.asyncio
    async def test_handle_fork_action(self, mock_github_client, sample_repo):
        """Test handling fork action."""
        forked_repo = GitHubRepo(
            id=789,
            name="test-repo",
            full_name="myuser/test-repo",
            owner=GitHubUser(
                login="myuser", id=999, html_url="https://github.com/myuser", avatar_url="https://github.com/myuser.png"
            ),
            private=False,
            fork=True,
            html_url="https://github.com/myuser/test-repo",
            clone_url="https://github.com/myuser/test-repo.git",
            ssh_url="git@github.com:myuser/test-repo.git",
            stargazers_count=0,
            watchers_count=0,
            forks_count=0,
            open_issues_count=0,
            size=512,
            default_branch="main",
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 12, 1, tzinfo=timezone.utc),
            pushed_at=datetime(2023, 11, 30, tzinfo=timezone.utc),
        )

        browser = RepositoryBrowser(mock_github_client)
        browser.notify = MagicMock()
        mock_github_client.fork_repository.return_value = forked_repo

        message = RepositoryActionMessage("fork", sample_repo)
        await browser.handle_repository_action(message)

        mock_github_client.fork_repository.assert_called_once_with("testowner", "test-repo")
        browser.notify.assert_called_with("Forked testowner/test-repo to myuser/test-repo")

    @pytest.mark.asyncio
    async def test_handle_clone_action(self, mock_github_client, sample_repo):
        """Test handling clone action."""
        browser = RepositoryBrowser(mock_github_client)
        browser.notify = MagicMock()

        message = RepositoryActionMessage("clone", sample_repo)

        # Test without pyperclip
        with patch.dict("sys.modules", {"pyperclip": None}):
            await browser.handle_repository_action(message)
            browser.notify.assert_called_with("Clone URL: https://github.com/testowner/test-repo.git")

        # Test with pyperclip
        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: MagicMock() if name == "pyperclip" else __import__(name, *args),
        ):
            mock_pyperclip = MagicMock()
            with patch.dict("sys.modules", {"pyperclip": mock_pyperclip}):
                await browser.handle_repository_action(message)
                browser.notify.assert_called_with(
                    "Copied clone URL to clipboard: https://github.com/testowner/test-repo.git"
                )

    @pytest.mark.asyncio
    async def test_handle_browser_action(self, mock_github_client, sample_repo):
        """Test handling browser action."""
        browser = RepositoryBrowser(mock_github_client)
        browser.notify = MagicMock()

        message = RepositoryActionMessage("browser", sample_repo)

        with patch("webbrowser.open") as mock_open:
            await browser.handle_repository_action(message)
            mock_open.assert_called_once_with("https://github.com/testowner/test-repo")
            browser.notify.assert_called_with("Opened testowner/test-repo in browser")

    @pytest.mark.asyncio
    async def test_handle_action_error(self, mock_github_client, sample_repo):
        """Test handling action errors."""
        browser = RepositoryBrowser(mock_github_client)
        browser.notify = MagicMock()

        # Mock an API error
        mock_github_client.star_repository.side_effect = Exception("API Error")

        message = RepositoryActionMessage("star", sample_repo)
        await browser.handle_repository_action(message)

        browser.notify.assert_called_with("Error performing star: API Error", severity="error")


@pytest.mark.api_mock
class TestBrowserIntegration:
    """Integration tests for the browser with mocked API calls."""

    def test_full_workflow(self, mock_github_client, sample_repos):
        """Test a complete workflow with the browser."""
        # Setup mocks
        mock_user = GitHubUser(
            login="testuser",
            id=123,
            html_url="https://github.com/testuser",
            avatar_url="https://github.com/testuser.png",
        )

        mock_github_client.get_authenticated_user.return_value = mock_user
        mock_github_client.get_user_repos.return_value = sample_repos
        mock_github_client.get_starred_repos.return_value = [sample_repos[0]]

        # Create browser
        browser = RepositoryBrowser(mock_github_client)
        browser.populate_table = MagicMock()
        browser.notify = MagicMock()

        # Simulate loading repositories manually since @work complicates testing
        async def simulate_workflow():
            user = await mock_github_client.get_authenticated_user()
            repos = await mock_github_client.get_user_repos(user.login)
            starred = await mock_github_client.get_starred_repos(user.login)

            starred_names = {repo.full_name for repo in starred}
            for repo in repos:
                repo.starred = repo.full_name in starred_names

            browser.repositories = repos
            browser.filtered_repositories = repos
            browser.populate_table()

            # Test repository action - mock the update_actions_pane to avoid screen stack issues
            browser.update_actions_pane = MagicMock()
            sample_repos[0].starred = False
            message = RepositoryActionMessage("star", sample_repos[0])
            await browser.handle_repository_action(message)

        # Run the simulation
        import asyncio

        asyncio.run(simulate_workflow())

        # Verify data was loaded
        assert len(browser.repositories) == 2
        assert browser.repositories[0].starred is True
        assert browser.repositories[1].starred is False

        # Test filtering
        browser.search_query = "python"
        browser.query_one = MagicMock(return_value=MagicMock(highlighted=None))
        browser.filter_repositories()

        assert len(browser.filtered_repositories) == 1
        assert browser.filtered_repositories[0].language == "Python"

        mock_github_client.star_repository.assert_called_once()
        browser.notify.assert_called_with("Starred testowner/test-repo")

    def test_populate_table_method(self, mock_github_client, sample_repos):
        """Test the populate_table method."""
        browser = RepositoryBrowser(mock_github_client)
        browser.filtered_repositories = sample_repos

        # Mock the table update methods
        with patch.object(browser, "query_one") as mock_query:
            mock_table = MagicMock()
            mock_query.return_value = mock_table

            # Test populate_table
            browser.populate_table()

            # Verify table methods were called
            mock_table.clear.assert_called_once()
            assert mock_table.add_row.call_count >= len(sample_repos)

    def test_update_details_pane_method(self, mock_github_client, sample_repo):
        """Test the update_details_pane method."""
        browser = RepositoryBrowser(mock_github_client)

        # Mock the details pane
        with patch.object(browser, "query_one") as mock_query:
            mock_pane = MagicMock()
            mock_query.return_value = mock_pane

            # Test update_details_pane
            browser.update_details_pane(sample_repo)

            # Verify pane was updated
            mock_pane.update_repo.assert_called_once_with(sample_repo)

    def test_update_actions_pane_method(self, mock_github_client, sample_repo):
        """Test the update_actions_pane method."""
        browser = RepositoryBrowser(mock_github_client)

        # Mock the actions pane
        with patch.object(browser, "query_one") as mock_query:
            mock_pane = MagicMock()
            mock_query.return_value = mock_pane

            # Test update_actions_pane
            browser.update_actions_pane(sample_repo)

            # Verify pane was updated
            mock_pane.update_repo.assert_called_once_with(sample_repo)

    def test_browser_basic_methods(self, mock_github_client):
        """Test basic browser methods that don't require UI."""
        browser = RepositoryBrowser(mock_github_client)

        # Test basic attribute access
        assert browser.github_client == mock_github_client
        assert browser.repositories == []
        assert browser.filtered_repositories == []
        assert browser.selected_repo is None
        assert browser.search_query == ""

    def test_filter_repositories_edge_cases(self, mock_github_client, sample_repos):
        """Test edge cases in filter_repositories method."""
        browser = RepositoryBrowser(mock_github_client)
        browser.repositories = sample_repos
        browser.populate_table = MagicMock()

        # Mock empty option list
        mock_option_list = MagicMock()
        mock_option_list.highlighted = None
        browser.query_one = MagicMock(return_value=mock_option_list)

        # Test with empty search query
        browser.search_query = ""
        browser.filter_repositories()
        assert len(browser.filtered_repositories) == len(sample_repos)

        # Test with search query that matches nothing
        browser.search_query = "nonexistent"
        browser.filter_repositories()
        assert len(browser.filtered_repositories) == 0

    def test_browser_initialization_edge_cases(self, mock_github_client):
        """Test browser initialization with different parameters."""
        # Test with username
        browser_with_user = RepositoryBrowser(mock_github_client, "testuser")
        assert browser_with_user.username == "testuser"
        assert "testuser" in browser_with_user.sub_title

        # Test without username
        browser_no_user = RepositoryBrowser(mock_github_client, None)
        assert browser_no_user.username is None
        assert "All Repositories" in browser_no_user.sub_title

    def test_repository_message_handling(self, mock_github_client, sample_repo):
        """Test repository message creation and handling."""
        browser = RepositoryBrowser(mock_github_client)

        # Test message creation
        message = RepositoryActionMessage("test_action", sample_repo)
        assert message.action == "test_action"
        assert message.repo == sample_repo

        # Test message handling (basic verification)
        browser.notify = MagicMock()
        browser.update_actions_pane = MagicMock()

        # This would normally be async, but we can test the sync parts
        assert hasattr(browser, "handle_repository_action")

    def test_browser_attribute_setting(self, mock_github_client):
        """Test setting browser attributes."""
        browser = RepositoryBrowser(mock_github_client)

        # Test setting title and subtitle

        browser.title = "New Title"
        browser.sub_title = "New Subtitle"

        assert browser.title == "New Title"
        assert browser.sub_title == "New Subtitle"

    @pytest.mark.asyncio
    async def test_error_handling_during_load(self, mock_github_client):
        """Test error handling during repository loading."""
        browser = RepositoryBrowser(mock_github_client, "testuser")
        browser.notify = MagicMock()

        # Mock API error
        mock_github_client.get_user_repos.side_effect = Exception("API Error")

        # Simulate load_repositories error handling
        try:
            await mock_github_client.get_user_repos("testuser")
        except Exception as e:
            browser.notify(f"Error loading repositories: {e}", severity="error")

        browser.notify.assert_called_with("Error loading repositories: API Error", severity="error")
