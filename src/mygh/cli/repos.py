"""Repository management CLI commands."""

import asyncio

import typer
from rich.console import Console

from ..api.client import GitHubClient
from ..api.models import GitHubIssue, GitHubRepo
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager
from ..utils.formatting import print_output

console = Console()
repos_app = typer.Typer(help="Repository management commands")
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


@repos_app.command("list")
@handle_exceptions  # type: ignore[misc]
async def repos_list(
    username: str | None = typer.Argument(
        None, help="GitHub username (defaults to authenticated user)"
    ),
    repo_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Repository type (all, public, private, owner, member)",
    ),
    sort: str = typer.Option(
        "updated",
        "--sort",
        "-s",
        help="Sort order (created, updated, pushed, full_name)",
    ),
    limit: int = typer.Option(
        30, "--limit", help="Maximum number of repositories to fetch"
    ),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json, csv)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """List repositories."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        repos: list[GitHubRepo] = []
        page = 1
        per_page = min(100, limit)

        while len(repos) < limit:
            batch = await client.get_user_repos(
                username=username,
                repo_type=repo_type,
                sort=sort,
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
            console.print("[yellow]No repositories found[/yellow]")
            return

        print_output(repos, format_type, output)
    finally:
        await client.close()


@repos_app.command("info")
@handle_exceptions  # type: ignore[misc]
async def repo_info(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Get repository information."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        # Get repo info by fetching user repos and filtering
        repos = await client.get_user_repos(username=owner, per_page=100)
        repo_info = next((r for r in repos if r.name == repo), None)

        if not repo_info:
            console.print(f"[red]Repository '{repo_name}' not found[/red]")
            raise typer.Exit(1) from None

        print_output([repo_info], format_type, output)
    finally:
        await client.close()


@repos_app.command("issues")
@handle_exceptions  # type: ignore[misc]
async def repo_issues(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    state: str = typer.Option(
        "open", "--state", "-s", help="Issue state (open, closed, all)"
    ),
    assignee: str | None = typer.Option(
        None, "--assignee", "-a", help="Filter by assignee (@me for yourself)"
    ),
    labels: str | None = typer.Option(
        None, "--labels", "-l", help="Filter by labels (comma-separated)"
    ),
    limit: int = typer.Option(30, "--limit", help="Maximum number of issues to fetch"),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """List repository issues."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        issues: list[GitHubIssue] = []
        page = 1
        per_page = min(100, limit)

        while len(issues) < limit:
            batch = await client.get_repo_issues(
                owner=owner,
                repo=repo,
                state=state,
                assignee=assignee,
                labels=labels,
                per_page=per_page,
                page=page,
            )

            if not batch:
                break

            issues.extend(batch)

            if len(batch) < per_page:
                break

            page += 1

        # Trim to requested limit
        issues = issues[:limit]

        if not issues:
            console.print("[yellow]No issues found[/yellow]")
            return

        print_output(issues, format_type, output)
    finally:
        await client.close()
