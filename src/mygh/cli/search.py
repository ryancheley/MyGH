"""Advanced search capabilities CLI commands."""

import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..api.client import GitHubClient
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager

console = Console()
search_app = typer.Typer(help="Advanced search capabilities")
config_manager = ConfigManager()


def handle_exceptions(func):  # type: ignore[no-untyped-def]
    """Decorator to handle common exceptions."""
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        try:
            return asyncio.run(func(*args, **kwargs))
        except AuthenticationError as e:
            console.print(f"[red]Authentication error: {e}[/red]")
            raise typer.Exit(1) from None
        except APIError as e:
            console.print(f"[red]API error: {e}[/red]")
            raise typer.Exit(1) from None
        except MyGHException as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from None
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled[/yellow]")
            raise typer.Exit(0) from None

    return wrapper


@search_app.command("repos")
@handle_exceptions  # type: ignore[misc]
async def search_repositories(
    query: str = typer.Argument(help="Search query"),
    sort: str = typer.Option("stars", "--sort", help="Sort by (stars, forks, updated)"),
    order: str = typer.Option("desc", "--order", help="Order (asc, desc)"),
    limit: int = typer.Option(20, "--limit", help="Maximum results"),
) -> None:
    """Search repositories."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        results = await client.search_repositories(query, sort, order, limit)
        
        if not results:
            console.print("[yellow]No repositories found[/yellow]")
            return

        table = Table(title=f"Repository Search: {query}")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white", max_width=50)
        table.add_column("Language", style="green")
        table.add_column("Stars", style="yellow", justify="right")

        for repo in results:
            description = repo.get("description", "") or ""
            if len(description) > 47:
                description = description[:47] + "..."
                
            table.add_row(
                repo.get("full_name", "N/A"),
                description,
                repo.get("language", "N/A") or "N/A",
                str(repo.get("stargazers_count", 0)),
            )

        console.print(table)

    finally:
        await client.close()


@search_app.command("users")
@handle_exceptions  # type: ignore[misc]
async def search_users(
    query: str = typer.Argument(help="Search query"),
    sort: str = typer.Option("followers", "--sort", help="Sort by (followers, repositories, joined)"),
    order: str = typer.Option("desc", "--order", help="Order (asc, desc)"),
    limit: int = typer.Option(20, "--limit", help="Maximum results"),
) -> None:
    """Search users."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        results = await client.search_users(query, sort, order, limit)
        
        if not results:
            console.print("[yellow]No users found[/yellow]")
            return

        table = Table(title=f"User Search: {query}")
        table.add_column("Login", style="cyan")
        table.add_column("Type", style="green")

        for user in results:
            table.add_row(
                user.get("login", "N/A"),
                user.get("type", "N/A"),
            )

        console.print(table)

    finally:
        await client.close()


if __name__ == "__main__":
    search_app()