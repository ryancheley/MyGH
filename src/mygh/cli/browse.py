"""Interactive repository browser CLI commands."""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from ..api.client import GitHubClient
from ..exceptions import APIError
from ..utils.config import ConfigManager
from ..utils.formatting import format_date, format_size

app = typer.Typer(help="Interactive repository browser")
console = Console()


class InteractiveBrowser:
    """Interactive repository browser with keyboard navigation."""
    
    def __init__(self, client: GitHubClient):
        self.client = client
        self.repositories = []
        self.current_page = 0
        self.per_page = 10
        self.selected_index = 0
        self.filter_text = ""
        
    async def load_repositories(self, username: Optional[str] = None):
        """Load repositories for browsing."""
        try:
            if username:
                self.repositories = await self.client.get_user_repos(username)
            else:
                self.repositories = await self.client.get_user_repos()
        except APIError as e:
            console.print(f"[red]Error loading repositories: {e}[/red]")
            return False
        return True
    
    def get_filtered_repos(self):
        """Get repositories filtered by search text."""
        if not self.filter_text:
            return self.repositories
        
        return [
            repo for repo in self.repositories
            if self.filter_text.lower() in repo.name.lower() or
               (repo.description and self.filter_text.lower() in repo.description.lower())
        ]
    
    def get_current_page_repos(self):
        """Get repositories for current page."""
        filtered = self.get_filtered_repos()
        start = self.current_page * self.per_page
        end = start + self.per_page
        return filtered[start:end], len(filtered)
    
    def display_repositories(self):
        """Display current page of repositories."""
        console.clear()
        
        repos, total = self.get_current_page_repos()
        
        # Header
        title = f"📚 Repository Browser"
        if self.filter_text:
            title += f" (filtered: '{self.filter_text}')"
        
        console.print(Panel(title, style="bold blue"))
        
        if not repos:
            console.print("[yellow]No repositories found.[/yellow]")
            return
        
        # Repository table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("", width=2)  # Selection indicator
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="dim")
        table.add_column("Language", style="green")
        table.add_column("Stars", justify="right", style="yellow")
        table.add_column("Updated", style="blue")
        
        for i, repo in enumerate(repos):
            indicator = "→" if i == self.selected_index else " "
            style = "bold" if i == self.selected_index else ""
            
            table.add_row(
                indicator,
                repo.name,
                repo.description[:50] + "..." if repo.description and len(repo.description) > 50 else repo.description or "",
                repo.language or "N/A",
                str(repo.stargazers_count),
                format_date(repo.updated_at),
                style=style
            )
        
        console.print(table)
        
        # Footer with navigation info
        page_info = f"Page {self.current_page + 1} • {total} total repositories"
        help_text = "↑↓: navigate • Enter: view details • f: filter • q: quit"
        
        console.print(f"\n[dim]{page_info}[/dim]")
        console.print(f"[dim]{help_text}[/dim]")
    
    async def show_repository_details(self, repo):
        """Show detailed information about a repository."""
        console.clear()
        
        # Repository header
        title = f"📁 {repo.name}"
        if repo.private:
            title += " 🔒"
        
        console.print(Panel(title, style="bold cyan"))
        
        # Basic info
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Field", style="bold")
        info_table.add_column("Value")
        
        info_table.add_row("Description", repo.description or "No description")
        info_table.add_row("Language", repo.language or "N/A")
        info_table.add_row("Stars", str(repo.stargazers_count))
        info_table.add_row("Forks", str(repo.forks_count))
        info_table.add_row("Issues", str(repo.open_issues_count))
        info_table.add_row("Size", format_size(repo.size * 1024))  # Size is in KB
        info_table.add_row("Created", format_date(repo.created_at))
        info_table.add_row("Updated", format_date(repo.updated_at))
        info_table.add_row("Clone URL", repo.clone_url)
        
        if repo.homepage:
            info_table.add_row("Homepage", repo.homepage)
        
        console.print(info_table)
        
        # Topics
        if repo.topics:
            console.print(f"\n[bold]Topics:[/bold] {', '.join(repo.topics)}")
        
        # Actions
        console.print("\n[dim]Press any key to return to browser...[/dim]")
        input()
    
    async def run(self, username: Optional[str] = None):
        """Run the interactive browser."""
        if not await self.load_repositories(username):
            return
        
        while True:
            self.display_repositories()
            
            # Get user input
            try:
                key = console.input("\n> ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                break
            
            repos, total = self.get_current_page_repos()
            
            if not repos:
                continue
                
            if key == "q" or key == "quit":
                break
            elif key == "f" or key == "filter":
                self.filter_text = Prompt.ask("Filter repositories", default=self.filter_text)
                self.current_page = 0
                self.selected_index = 0
            elif key == "c" or key == "clear":
                self.filter_text = ""
                self.current_page = 0
                self.selected_index = 0
            elif key == "j" or key == "down":
                if self.selected_index < len(repos) - 1:
                    self.selected_index += 1
            elif key == "k" or key == "up":
                if self.selected_index > 0:
                    self.selected_index -= 1
            elif key == "n" or key == "next":
                if (self.current_page + 1) * self.per_page < total:
                    self.current_page += 1
                    self.selected_index = 0
            elif key == "p" or key == "prev":
                if self.current_page > 0:
                    self.current_page -= 1
                    self.selected_index = 0
            elif key == "" or key == "enter":
                if repos and self.selected_index < len(repos):
                    await self.show_repository_details(repos[self.selected_index])
            elif key == "h" or key == "help":
                console.print(Panel(
                    "j/down: Move down\nk/up: Move up\nn/next: Next page\np/prev: Previous page\nf/filter: Filter repositories\nc/clear: Clear filter\nenter: View details\nq/quit: Exit",
                    title="Help",
                    style="yellow"
                ))
                input("Press any key to continue...")


@app.command()
def repos(
    username: Optional[str] = typer.Argument(None, help="Username to browse repositories for")
):
    """Launch interactive repository browser."""
    async def _browse():
        config_manager = ConfigManager()
        config = config_manager.get_config()
        async with GitHubClient(config.github_token) as client:
            browser = InteractiveBrowser(client)
            await browser.run(username)
    
    try:
        asyncio.run(_browse())
    except KeyboardInterrupt:
        console.print("\n[yellow]Browser closed.[/yellow]")


if __name__ == "__main__":
    app()