"""Team management CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..api.client import GitHubClient
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager

console = Console()
teams_app = typer.Typer(help="Team management commands")
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


@teams_app.command("list")
@handle_exceptions  # type: ignore[misc]
async def list_teams(
    org_name: str = typer.Argument(help="Organization name"),
) -> None:
    """List organization teams."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        teams = await client.get_organization_teams(org_name)

        if not teams:
            console.print("[yellow]No teams found[/yellow]")
            return

        table = Table(title=f"Teams in {org_name}")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="white", max_width=50)
        table.add_column("Privacy", style="green")
        table.add_column("Members", style="yellow", justify="right")

        for team in teams:
            description = team.get("description", "") or ""
            if len(description) > 47:
                description = description[:47] + "..."

            table.add_row(
                team.get("name", "N/A"),
                description,
                team.get("privacy", "N/A"),
                str(team.get("members_count", 0)),
            )

        console.print(table)

    finally:
        await client.close()


@teams_app.command("members")
@handle_exceptions  # type: ignore[misc]
async def list_team_members(
    org_name: str = typer.Argument(help="Organization name"),
    team_slug: str = typer.Argument(help="Team slug"),
) -> None:
    """List team members."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        members = await client.get_team_members(org_name, team_slug)

        if not members:
            console.print("[yellow]No team members found[/yellow]")
            return

        table = Table(title=f"Members of {org_name}/{team_slug}")
        table.add_column("Login", style="cyan")
        table.add_column("Role", style="green")

        for member in members:
            table.add_row(
                member.get("login", "N/A"),
                member.get("role", "member"),
            )

        console.print(table)

    finally:
        await client.close()


if __name__ == "__main__":
    teams_app()
