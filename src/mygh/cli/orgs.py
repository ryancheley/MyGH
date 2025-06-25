"""Organization management CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..api.client import GitHubClient
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager

console = Console()
orgs_app = typer.Typer(help="Organization management commands")
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


@orgs_app.command("list")
@handle_exceptions  # type: ignore[misc]
async def list_orgs() -> None:
    """List user organizations."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        orgs = await client.get_user_organizations()

        if not orgs:
            console.print("[yellow]No organizations found[/yellow]")
            return

        table = Table(title="Organizations")
        table.add_column("Login", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")

        for org in orgs:
            table.add_row(
                org.get("login", "N/A"),
                org.get("name", "N/A") or "N/A",
                org.get("description", "N/A") or "N/A",
            )

        console.print(table)

    finally:
        await client.close()


@orgs_app.command("members")
@handle_exceptions  # type: ignore[misc]
async def list_members(
    org_name: str = typer.Argument(help="Organization name"),
    role: str | None = typer.Option(None, "--role", help="Filter by role (admin, member)"),
) -> None:
    """List organization members."""
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        members = await client.get_organization_members(org_name, role)

        if not members:
            console.print("[yellow]No members found[/yellow]")
            return

        table = Table(title=f"Members of {org_name}")
        table.add_column("Login", style="cyan")
        table.add_column("Type", style="green")

        for member in members:
            table.add_row(
                member.get("login", "N/A"),
                member.get("type", "N/A"),
            )

        console.print(table)

    finally:
        await client.close()


if __name__ == "__main__":
    orgs_app()
