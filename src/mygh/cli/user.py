"""User-related CLI commands."""

import asyncio

import typer
from rich.console import Console

from ..api.client import GitHubClient
from ..api.models import GitHubRepo
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager
from ..utils.formatting import print_output

console = Console()
user_app = typer.Typer(help="User-related commands")
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
            console.print("\n[yellow]To authenticate:[/yellow]")
            console.print("  1. Set GITHUB_TOKEN environment variable")
            console.print("  2. Or run: gh auth login")
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
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            raise typer.Exit(1) from None

    return wrapper


@user_app.command("info")
@handle_exceptions  # type: ignore[misc]
async def user_info(
    username: str | None = typer.Argument(
        None, help="GitHub username (defaults to authenticated user)"
    ),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Get user information."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        user = await client.get_user(username)
        print_output(user, format_type, output)
    finally:
        await client.close()


@user_app.command("starred")
@handle_exceptions  # type: ignore[misc]
async def user_starred(
    username: str | None = typer.Argument(
        None, help="GitHub username (defaults to authenticated user)"
    ),
    language: str | None = typer.Option(
        None, "--language", "-l", help="Filter by programming language"
    ),
    limit: int = typer.Option(
        30, "--limit", help="Maximum number of repositories to fetch"
    ),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json, csv)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """List starred repositories."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        repos: list[GitHubRepo] = []
        page = 1
        per_page = min(100, limit)

        while len(repos) < limit:
            batch = await client.get_starred_repos(
                username=username,
                language=language,
                per_page=per_page,
                page=page,
            )

            if not batch:
                break

            repos.extend(batch)

            if len(batch) < per_page:
                break

            page += 1

        # Trim to requested limit
        repos = repos[:limit]

        if not repos:
            console.print("[yellow]No starred repositories found[/yellow]")
            return

        print_output(repos, format_type, output, is_starred=True)
    finally:
        await client.close()


@user_app.command("gists")
@handle_exceptions  # type: ignore[misc]
async def user_gists(
    username: str | None = typer.Argument(
        None, help="GitHub username (defaults to authenticated user)"
    ),
    public_only: bool = typer.Option(False, "--public", help="Show only public gists"),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """List user gists."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        gists = await client.get_user_gists(username)

        if public_only:
            gists = [gist for gist in gists if gist.public]

        if not gists:
            console.print("[yellow]No gists found[/yellow]")
            return

        print_output(gists, format_type, output)
    finally:
        await client.close()
