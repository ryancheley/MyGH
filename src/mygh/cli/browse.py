"""Interactive repository browser CLI commands."""

import asyncio

import typer
from rich.console import Console

from ..api.client import GitHubClient
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..tui.browser import RepositoryBrowser

console = Console()
browse_app = typer.Typer(help="Interactive repository browser")


@browse_app.command("repos")
def browse_repositories(
    username: str | None = typer.Option(
        None, "--user", "-u", help="Username to browse repositories for (defaults to authenticated user)"
    ),
) -> None:
    """Launch interactive repository browser."""

    async def run_browser() -> None:
        try:
            async with GitHubClient() as client:
                app = RepositoryBrowser(client, username)
                await app.run_async()
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
            console.print("\n[yellow]Browser closed[/yellow]")
        except Exception as e:
            console.print(f"[red]Error running browser: {e}[/red]")
            raise typer.Exit(1) from None

    asyncio.run(run_browser())


@browse_app.command("starred")
def browse_starred(
    username: str | None = typer.Option(
        None, "--user", "-u", help="Username to browse starred repositories for (defaults to authenticated user)"
    ),
) -> None:
    """Launch interactive browser for starred repositories only."""

    async def run_starred_browser() -> None:
        try:
            async with GitHubClient() as client:
                # Create a specialized browser for starred repos
                app = RepositoryBrowser(client, username)
                app.title = "MyGH - Interactive Starred Repositories Browser"
                app.sub_title = f"Starred by: {username}" if username else "Your Starred Repositories"

                # Load starred repositories and set them
                if username:
                    repos = await client.get_starred_repos(username)
                else:
                    user = await client.get_authenticated_user()
                    repos = await client.get_starred_repos(user.login)

                # Mark all as starred since we're only showing starred repos
                for repo in repos:
                    repo.starred = True

                app.repositories = repos
                app.filtered_repositories = repos

                await app.run_async()

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
            console.print("\n[yellow]Browser closed[/yellow]")
        except Exception as e:
            console.print(f"[red]Error running starred browser: {e}[/red]")
            raise typer.Exit(1) from None

    asyncio.run(run_starred_browser())
