"""Notification management CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..api.client import GitHubClient
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager

console = Console()
notifications_app = typer.Typer(help="Notification management commands")
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


@notifications_app.command("list")
@handle_exceptions  # type: ignore[misc]
async def list_notifications(
    all_notifications: bool = typer.Option(False, "--all", help="Include read notifications"),
    participating: bool = typer.Option(False, "--participating", help="Only participating notifications"),
    limit: int = typer.Option(20, "--limit", help="Maximum notifications"),
) -> None:
    """List notifications."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        notifications = await client.get_notifications(all_notifications, participating, limit)

        if not notifications:
            console.print("[yellow]No notifications found[/yellow]")
            return

        table = Table(title="Notifications")
        table.add_column("Repository", style="cyan")
        table.add_column("Subject", style="white", max_width=50)
        table.add_column("Type", style="green")
        table.add_column("Unread", style="yellow")

        for notification in notifications:
            subject_title = notification.get("subject", {}).get("title", "N/A")
            if len(subject_title) > 47:
                subject_title = subject_title[:47] + "..."

            table.add_row(
                notification.get("repository", {}).get("full_name", "N/A"),
                subject_title,
                notification.get("subject", {}).get("type", "N/A"),
                "Yes" if notification.get("unread", False) else "No",
            )

        console.print(table)

    finally:
        await client.close()


@notifications_app.command("mark-read")
@handle_exceptions  # type: ignore[misc]
async def mark_read(
    repo_name: str | None = typer.Option(None, "--repo", help="Repository (owner/repo format)"),
) -> None:
    """Mark notifications as read."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        if repo_name:
            if "/" not in repo_name:
                console.print("[red]Repository name must be in 'owner/repo' format[/red]")
                raise typer.Exit(1)
            owner, repo = repo_name.split("/", 1)
            await client.mark_notifications_read(owner, repo)
            console.print(f"[green]Marked notifications as read for {repo_name}[/green]")
        else:
            await client.mark_all_notifications_read()
            console.print("[green]Marked all notifications as read[/green]")

    finally:
        await client.close()


if __name__ == "__main__":
    notifications_app()
