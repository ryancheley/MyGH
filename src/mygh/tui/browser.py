"""Interactive repository browser using Textual."""

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    Static,
)
from textual.widgets.option_list import Option

from ..api.client import GitHubClient
from ..api.models import GitHubRepo


class RepositoryDetailsPane(Static):
    """Widget to display detailed repository information."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repo: GitHubRepo | None = None

    def update_repo(self, repo: GitHubRepo) -> None:
        """Update the displayed repository details."""
        self.repo = repo
        self.update_display()

    def update_display(self) -> None:
        """Update the display with current repository information."""
        if not self.repo:
            self.update("Select a repository to view details")
            return

        repo = self.repo
        details = []
        details.append(f"[bold cyan]{repo.full_name}[/bold cyan]")

        if repo.description:
            details.append(f"\n{repo.description}")

        details.append(f"\n[bold]Language:[/bold] {repo.language or 'N/A'}")
        details.append(f"[bold]Stars:[/bold] {repo.stargazers_count}")
        details.append(f"[bold]Forks:[/bold] {repo.forks_count}")
        details.append(f"[bold]Issues:[/bold] {repo.open_issues_count}")
        details.append(f"[bold]License:[/bold] {repo.license.name if repo.license else 'N/A'}")
        details.append(f"[bold]Private:[/bold] {'Yes' if repo.private else 'No'}")
        details.append(f"[bold]Fork:[/bold] {'Yes' if repo.fork else 'No'}")

        if repo.homepage:
            details.append(f"[bold]Homepage:[/bold] {repo.homepage}")

        details.append(f"[bold]Clone URL:[/bold] {repo.clone_url}")
        details.append(f"[bold]HTML URL:[/bold] {repo.html_url}")

        if repo.created_at:
            details.append(f"[bold]Created:[/bold] {repo.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if repo.updated_at:
            details.append(f"[bold]Updated:[/bold] {repo.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if repo.pushed_at:
            details.append(f"[bold]Last Push:[/bold] {repo.pushed_at.strftime('%Y-%m-%d %H:%M:%S')}")

        self.update("\n".join(details))


class QuickActionsPane(Container):
    """Widget for quick actions on repositories."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.repo: GitHubRepo | None = None

    def compose(self) -> ComposeResult:
        """Compose the quick actions interface."""
        yield Label("Quick Actions:", id="actions-title")
        yield Button("🌟 Star/Unstar", id="star-btn", variant="primary")
        yield Button("👁 Watch/Unwatch", id="watch-btn", variant="default")
        yield Button("🍴 Fork", id="fork-btn", variant="default")
        yield Button("📋 Clone URL", id="clone-btn", variant="default")
        yield Button("🌍 Open in Browser", id="browser-btn", variant="default")
        yield Button("📝 Issues", id="issues-btn", variant="default")
        yield Button("🔀 Pull Requests", id="prs-btn", variant="default")

    def update_repo(self, repo: GitHubRepo) -> None:
        """Update the current repository for actions."""
        self.repo = repo

        # Update button states based on repository
        star_btn = self.query_one("#star-btn", Button)
        if hasattr(repo, "starred") and repo.starred:
            star_btn.label = "⭐ Unstar"
        else:
            star_btn.label = "🌟 Star"

    @on(Button.Pressed, "#star-btn")
    def handle_star(self) -> None:
        """Handle star/unstar action."""
        if self.repo:
            self.app.post_message(RepositoryActionMessage("star", self.repo))

    @on(Button.Pressed, "#watch-btn")
    def handle_watch(self) -> None:
        """Handle watch/unwatch action."""
        if self.repo:
            self.app.post_message(RepositoryActionMessage("watch", self.repo))

    @on(Button.Pressed, "#fork-btn")
    def handle_fork(self) -> None:
        """Handle fork action."""
        if self.repo:
            self.app.post_message(RepositoryActionMessage("fork", self.repo))

    @on(Button.Pressed, "#clone-btn")
    def handle_clone(self) -> None:
        """Handle clone URL copy action."""
        if self.repo:
            self.app.post_message(RepositoryActionMessage("clone", self.repo))

    @on(Button.Pressed, "#browser-btn")
    def handle_browser(self) -> None:
        """Handle open in browser action."""
        if self.repo:
            self.app.post_message(RepositoryActionMessage("browser", self.repo))

    @on(Button.Pressed, "#issues-btn")
    def handle_issues(self) -> None:
        """Handle view issues action."""
        if self.repo:
            self.app.post_message(RepositoryActionMessage("issues", self.repo))

    @on(Button.Pressed, "#prs-btn")
    def handle_prs(self) -> None:
        """Handle view pull requests action."""
        if self.repo:
            self.app.post_message(RepositoryActionMessage("prs", self.repo))


class RepositoryActionMessage(Message):
    """Message for repository actions."""

    def __init__(self, action: str, repo: GitHubRepo) -> None:
        super().__init__()
        self.action = action
        self.repo = repo


class RepositoryBrowser(App[None]):
    """Interactive repository browser application."""

    CSS = """
    #main-container {
        height: 100%;
    }

    #left-panel {
        width: 60%;
        border-right: solid $accent;
    }

    #right-panel {
        width: 40%;
    }

    #search-container {
        height: 3;
        padding: 1;
    }

    #repo-table {
        height: 1fr;
    }

    #details-pane {
        height: 60%;
        padding: 1;
        border-bottom: solid $accent;
    }

    #actions-pane {
        height: 40%;
        padding: 1;
    }

    #actions-title {
        margin-bottom: 1;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
    }

    #filter-options {
        height: 10;
        width: 100%;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("f", "focus_search", "Focus Search"),
        ("escape", "clear_search", "Clear Search"),
    ]

    repositories: reactive[list[GitHubRepo]] = reactive([])
    filtered_repositories: reactive[list[GitHubRepo]] = reactive([])
    selected_repo: reactive[GitHubRepo | None] = reactive(None)
    search_query: reactive[str] = reactive("")

    def __init__(self, github_client: GitHubClient, username: str | None = None) -> None:
        super().__init__()
        self.github_client = github_client
        self.username = username
        self.title = "MyGH - Interactive Repository Browser"
        self.sub_title = f"User: {username}" if username else "All Repositories"

    def compose(self) -> ComposeResult:
        """Compose the user interface."""
        yield Header()

        with Container(id="main-container"):
            with Vertical(id="left-panel"):
                with Container(id="search-container"):
                    yield Input(placeholder="Search repositories...", id="search-input")
                    yield OptionList(
                        Option("All repositories", id="all"),
                        Option("Starred only", id="starred"),
                        Option("Owned only", id="owned"),
                        Option("Forked only", id="forked"),
                        Option("With issues", id="issues"),
                        id="filter-options",
                    )

                yield DataTable(id="repo-table")

            with Vertical(id="right-panel"):
                yield RepositoryDetailsPane(id="details-pane")
                yield QuickActionsPane(id="actions-pane")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application."""
        self.setup_table()
        self.load_repositories()

    def setup_table(self) -> None:
        """Setup the repository table."""
        table = self.query_one("#repo-table", DataTable)
        table.add_columns("Name", "Description", "Language", "Stars", "Forks", "Updated")
        table.cursor_type = "row"
        table.zebra_stripes = True

    @work(exclusive=True)
    async def load_repositories(self) -> None:
        """Load repositories from GitHub API."""
        try:
            if self.username:
                repos = await self.github_client.get_user_repos(self.username)
                starred = await self.github_client.get_starred_repos(self.username)

                # Mark starred repositories
                starred_names = {repo.full_name for repo in starred}
                for repo in repos:
                    repo.starred = repo.full_name in starred_names
            else:
                # For now, get authenticated user's repos
                user = await self.github_client.get_authenticated_user()
                repos = await self.github_client.get_user_repos(user.login)
                starred = await self.github_client.get_starred_repos(user.login)

                starred_names = {repo.full_name for repo in starred}
                for repo in repos:
                    repo.starred = repo.full_name in starred_names

            self.repositories = repos
            self.filtered_repositories = repos
            self.populate_table()

        except Exception as e:
            self.notify(f"Error loading repositories: {e}", severity="error")

    def populate_table(self) -> None:
        """Populate the table with repository data."""
        table = self.query_one("#repo-table", DataTable)
        table.clear()

        for repo in self.filtered_repositories:
            description = repo.description or ""
            if len(description) > 40:
                description = description[:37] + "..."

            updated = repo.updated_at.strftime("%Y-%m-%d") if repo.updated_at else "N/A"

            table.add_row(
                repo.name,
                description,
                repo.language or "",
                str(repo.stargazers_count),
                str(repo.forks_count),
                updated,
                key=repo.full_name,
            )

    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle repository selection."""
        self.query_one("#repo-table", DataTable)
        row_key = event.row_key

        # Find the repository by full_name
        selected_repo = None
        for repo in self.filtered_repositories:
            if repo.full_name == row_key:
                selected_repo = repo
                break

        if selected_repo:
            self.selected_repo = selected_repo
            self.update_details_pane(selected_repo)
            self.update_actions_pane(selected_repo)

    def update_details_pane(self, repo: GitHubRepo) -> None:
        """Update the repository details pane."""
        details_pane = self.query_one("#details-pane", RepositoryDetailsPane)
        details_pane.update_repo(repo)

    def update_actions_pane(self, repo: GitHubRepo) -> None:
        """Update the quick actions pane."""
        actions_pane = self.query_one("#actions-pane", QuickActionsPane)
        actions_pane.update_repo(repo)

    @on(Input.Changed, "#search-input")
    def handle_search(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.search_query = event.value.lower()
        self.filter_repositories()

    @on(OptionList.OptionSelected, "#filter-options")
    def handle_filter_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle filter option selection."""
        self.filter_repositories()

    def filter_repositories(self) -> None:
        """Filter repositories based on search query and selected filters."""
        filtered = self.repositories[:]

        # Apply search filter
        if self.search_query:
            filtered = [
                repo
                for repo in filtered
                if (
                    self.search_query in repo.name.lower()
                    or (repo.description and self.search_query in repo.description.lower())
                    or (repo.language and self.search_query in repo.language.lower())
                )
            ]

        # Apply category filter
        filter_options = self.query_one("#filter-options", OptionList)
        if filter_options.highlighted is not None:
            selected_filter = filter_options.get_option_at_index(filter_options.highlighted)
            if selected_filter:
                filter_id = selected_filter.id

                if filter_id == "starred":
                    filtered = [repo for repo in filtered if getattr(repo, "starred", False)]
                elif filter_id == "owned":
                    filtered = [repo for repo in filtered if not repo.fork]
                elif filter_id == "forked":
                    filtered = [repo for repo in filtered if repo.fork]
                elif filter_id == "issues":
                    filtered = [repo for repo in filtered if repo.open_issues_count > 0]

        self.filtered_repositories = filtered
        self.populate_table()

    @on(RepositoryActionMessage)
    async def handle_repository_action(self, message: RepositoryActionMessage) -> None:
        """Handle repository actions."""
        action = message.action
        repo = message.repo

        try:
            if action == "star":
                if getattr(repo, "starred", False):
                    await self.github_client.unstar_repository(repo.owner.login, repo.name)
                    repo.starred = False
                    self.notify(f"Unstarred {repo.full_name}")
                else:
                    await self.github_client.star_repository(repo.owner.login, repo.name)
                    repo.starred = True
                    self.notify(f"Starred {repo.full_name}")

                self.update_actions_pane(repo)

            elif action == "fork":
                forked_repo = await self.github_client.fork_repository(repo.owner.login, repo.name)
                self.notify(f"Forked {repo.full_name} to {forked_repo.full_name}")

            elif action == "clone":
                # Copy clone URL to clipboard and show notification
                try:
                    import pyperclip

                    pyperclip.copy(repo.clone_url)
                    self.notify(f"Copied clone URL to clipboard: {repo.clone_url}")
                except ImportError:
                    self.notify(f"Clone URL: {repo.clone_url}")
                except Exception:
                    self.notify(f"Clone URL: {repo.clone_url}")

            elif action == "browser":
                import webbrowser

                webbrowser.open(repo.html_url)
                self.notify(f"Opened {repo.full_name} in browser")

            elif action == "issues":
                self.notify(f"Viewing issues for {repo.full_name} (feature coming soon)")

            elif action == "prs":
                self.notify(f"Viewing pull requests for {repo.full_name} (feature coming soon)")

            elif action == "watch":
                self.notify(f"Watch/unwatch for {repo.full_name} (feature coming soon)")

        except Exception as e:
            self.notify(f"Error performing {action}: {e}", severity="error")

    def action_refresh(self) -> None:
        """Refresh repository data."""
        self.load_repositories()
        self.notify("Refreshing repositories...")

    def action_focus_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def action_clear_search(self) -> None:
        """Clear the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
