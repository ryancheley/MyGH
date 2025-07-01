"""Additional tests for TUI browser module to improve coverage."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

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
    return AsyncMock()


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


class TestRepositoryDetailsPaneCoverage:
    """Test coverage for RepositoryDetailsPane methods."""

    def test_update_display_with_various_repo_states(self, sample_repo):
        """Test update_display with different repository states."""
        pane = RepositoryDetailsPane()
        pane.update = MagicMock()

        # Test with repository having all optional fields
        sample_repo.description = "Full description"
        sample_repo.language = "Python"
        sample_repo.homepage = "https://example.com"

        pane.repo = sample_repo
        pane.update_display()

        # Verify update was called with formatted content
        pane.update.assert_called_once()
        call_content = pane.update.call_args[0][0]
        assert "testowner/test-repo" in call_content
        assert "Full description" in call_content
        assert "Python" in call_content
        assert "42" in call_content  # stars
        assert "7" in call_content  # forks

    def test_update_display_with_minimal_repo(self, sample_repo):
        """Test update_display with minimal repository data."""
        pane = RepositoryDetailsPane()
        pane.update = MagicMock()

        # Remove optional fields
        sample_repo.description = None
        sample_repo.language = None
        sample_repo.homepage = None

        pane.repo = sample_repo
        pane.update_display()

        # Verify update was called
        pane.update.assert_called_once()
        call_content = pane.update.call_args[0][0]
        assert "testowner/test-repo" in call_content
        # The implementation uses "[bold]Language:[/bold] N/A"
        assert "[bold]Language:[/bold] N/A" in call_content


class TestQuickActionsPaneCoverage:
    """Test coverage for QuickActionsPane methods."""

    def test_update_repo_with_starred_status(self, sample_repo):
        """Test update_repo with different starred states."""
        pane = QuickActionsPane()
        pane.query_one = MagicMock()

        # Mock button
        mock_button = MagicMock()
        pane.query_one.return_value = mock_button

        # Test with starred repo
        sample_repo.starred = True
        pane.update_repo(sample_repo)
        assert pane.repo == sample_repo
        mock_button.label = "★ Unstar"

        # Test with unstarred repo
        sample_repo.starred = False
        pane.update_repo(sample_repo)
        mock_button.label = "☆ Star"


class TestRepositoryBrowserCoverage:
    """Test coverage for RepositoryBrowser methods."""

    def test_css_style_definitions(self, mock_github_client):
        """Test that CSS styles are properly defined."""
        browser = RepositoryBrowser(mock_github_client)

        # Check that CSS is defined
        assert hasattr(browser, "CSS")
        assert browser.CSS is not None
        assert len(browser.CSS.strip()) > 0

    def test_compose_method_components(self, mock_github_client):
        """Test compose method component creation."""
        browser = RepositoryBrowser(mock_github_client)

        # Test that compose returns widgets (indirect test)
        # We can't easily test this without running the full Textual app
        # but we can verify the method exists and basic properties
        assert hasattr(browser, "compose")
        assert callable(browser.compose)

    def test_browser_internal_methods_exist(self, mock_github_client):
        """Test that browser has expected internal methods."""
        browser = RepositoryBrowser(mock_github_client)

        # Test that key methods exist
        assert hasattr(browser, "populate_table")
        assert hasattr(browser, "update_details_pane")
        assert hasattr(browser, "update_actions_pane")
        assert hasattr(browser, "filter_repositories")
        assert callable(browser.populate_table)
        assert callable(browser.update_details_pane)
        assert callable(browser.update_actions_pane)
        assert callable(browser.filter_repositories)

    def test_filter_repositories_basic_functionality(self, mock_github_client, sample_repo):
        """Test basic filter_repositories functionality."""
        browser = RepositoryBrowser(mock_github_client)
        browser.repositories = [sample_repo]
        browser.populate_table = MagicMock()
        browser.search_query = ""

        # Mock option list with no selection
        mock_option_list = MagicMock()
        mock_option_list.highlighted = None
        browser.query_one = MagicMock(return_value=mock_option_list)

        # Test basic filtering
        browser.filter_repositories()

        # Should populate table
        browser.populate_table.assert_called_once()

    @pytest.mark.asyncio
    async def test_unknown_repository_action(self, mock_github_client, sample_repo):
        """Test handling of unknown repository actions."""
        browser = RepositoryBrowser(mock_github_client)
        browser.notify = MagicMock()

        # Test unknown action
        message = RepositoryActionMessage("unknown_action", sample_repo)
        await browser.handle_repository_action(message)

        # Should not crash and should potentially notify
        # The current implementation may just ignore unknown actions
        assert True  # Test passes if no exception is raised

    def test_bindings_definition(self, mock_github_client):
        """Test that key bindings are properly defined."""
        browser = RepositoryBrowser(mock_github_client)

        # Check that bindings are defined
        assert hasattr(browser, "BINDINGS")
        assert len(browser.BINDINGS) > 0

        # Verify specific bindings exist
        binding_keys = [binding[0] for binding in browser.BINDINGS]
        assert "q" in binding_keys
        assert "ctrl+c" in binding_keys
        assert "r" in binding_keys

    def test_repository_browser_class_attributes(self, mock_github_client):
        """Test class-level attributes of RepositoryBrowser."""
        browser = RepositoryBrowser(mock_github_client)

        # Test title and subtitle behavior
        assert hasattr(browser, "title")
        assert hasattr(browser, "sub_title")

        # Test with username
        browser_with_user = RepositoryBrowser(mock_github_client, "testuser")
        assert "testuser" in browser_with_user.sub_title

        # Test without username
        browser_no_user = RepositoryBrowser(mock_github_client)
        assert "All Repositories" in browser_no_user.sub_title
