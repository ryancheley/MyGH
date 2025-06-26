"""Search CLI commands for MyGH."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..api.client import GitHubClient
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager
from ..utils.formatting import format_json

console = Console()


def validate_repo_sort(sort: str | None) -> None:
    """Validate repository sort option."""
    valid_sorts = ["stars", "forks", "help-wanted-issues", "updated"]
    if sort is not None and sort not in valid_sorts:
        console.print(f"[red]Invalid sort option: {sort}[/red]")
        console.print("Valid options: stars, forks, help-wanted-issues, updated")
        raise typer.Exit(1)


def validate_user_sort(sort: str | None) -> None:
    """Validate user sort option."""
    if sort is not None and sort not in ["followers", "repositories", "joined"]:
        console.print(f"[red]Invalid sort option: {sort}[/red]")
        console.print("Valid options: followers, repositories, joined")
        raise typer.Exit(1)


def validate_order(order: str) -> None:
    """Validate order option."""
    if order not in ["asc", "desc"]:
        console.print(f"[red]Invalid order option: {order}[/red]")
        console.print("Valid options: asc, desc")
        raise typer.Exit(1)


def handle_exceptions(func):  # type: ignore[no-untyped-def]
    """Decorator to handle common exceptions."""

    def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
        try:
            if asyncio.iscoroutinefunction(func):
                return asyncio.run(func(*args, **kwargs))
            else:
                return func(*args, **kwargs)
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


# Create search app
search_app = typer.Typer(
    name="search",
    help="Advanced search capabilities",
    rich_markup_mode="rich",
)


@search_app.command("repos")
def search_repos(
    query: str = typer.Argument(..., help="Search query"),
    sort: str | None = typer.Option(
        None,
        "--sort",
        help="Sort results by (stars, forks, help-wanted-issues, updated)",
    ),
    order: str = typer.Option(
        "desc",
        "--order",
        help="Sort order (asc, desc)",
    ),
    limit: int = typer.Option(
        30,
        "--limit",
        min=1,
        help="Number of results to return",
    ),
    format_type: str | None = typer.Option(
        None,
        "--format",
        help="Output format (table, json)",
    ),
    output: str = typer.Option(
        None,
        "--output",
        help="Output file path",
    ),
) -> None:
    """Search repositories on GitHub."""
    # Validate options before proceeding
    validate_repo_sort(sort)
    validate_order(order)

    async def _search_repos() -> None:
        config_manager = ConfigManager()
        format_type_final = format_type or config_manager.load_config().output_format

        # Validate format
        if format_type_final not in ["table", "json"]:
            console.print(f"[red]Invalid format: {format_type_final}[/red]")
            console.print("Available formats: table, json")
            raise typer.Exit(1)

        async with GitHubClient() as client:
            result = await client.search_repositories(
                query=query,
                sort=sort,
                order=order,
                per_page=limit,
            )

            if format_type_final == "table":
                table = Table(title=f"Repository Search Results: {query}")
                table.add_column("Repository")
                table.add_column("Description")
                table.add_column("Language")
                table.add_column("Stars", justify="right")
                table.add_column("Forks", justify="right")
                table.add_column("Updated")

                for repo in result.items:
                    table.add_row(
                        f"[bold cyan]{repo.full_name}[/bold cyan]",
                        repo.description or "[dim]No description[/dim]",
                        repo.language or "[dim]Unknown[/dim]",
                        str(repo.stargazers_count),
                        str(repo.forks_count),
                        repo.updated_at.strftime("%Y-%m-%d"),
                    )

                console.print(table)
                console.print(f"\n[dim]Total results: {result.total_count}[/dim]")
            else:
                output_data = {
                    "total_count": result.total_count,
                    "incomplete_results": result.incomplete_results,
                    "items": [repo.model_dump() for repo in result.items],
                }

                if output:
                    formatted_output = format_json(output_data)
                    with open(output, "w") as f:
                        f.write(formatted_output)
                    console.print(f"[green]Results written to {output}[/green]")
                else:
                    console.print(format_json(output_data))

    try:
        asyncio.run(_search_repos())
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


@search_app.command("users")
def search_users(
    query: str = typer.Argument(..., help="Search query"),
    sort: str | None = typer.Option(
        None,
        "--sort",
        help="Sort results by (followers, repositories, joined)",
    ),
    order: str = typer.Option(
        "desc",
        "--order",
        help="Sort order (asc, desc)",
    ),
    limit: int = typer.Option(
        30,
        "--limit",
        min=1,
        help="Number of results to return",
    ),
    format_type: str | None = typer.Option(
        None,
        "--format",
        help="Output format (table, json)",
    ),
    output: str = typer.Option(
        None,
        "--output",
        help="Output file path",
    ),
) -> None:
    """Search users on GitHub."""
    # Validate options before proceeding
    validate_user_sort(sort)
    validate_order(order)

    async def _search_users() -> None:
        config_manager = ConfigManager()
        format_type_final = format_type or config_manager.load_config().output_format

        # Validate format
        if format_type_final not in ["table", "json"]:
            console.print(f"[red]Invalid format: {format_type_final}[/red]")
            console.print("Available formats: table, json")
            raise typer.Exit(1)

        async with GitHubClient() as client:
            result = await client.search_users(
                query=query,
                sort=sort,
                order=order,
                per_page=limit,
            )

            if format_type_final == "table":
                table = Table(title=f"User Search Results: {query}")
                table.add_column("Username")
                table.add_column("Name")
                table.add_column("Company")
                table.add_column("Location")
                table.add_column("Followers", justify="right")
                table.add_column("Public Repos", justify="right")

                for user in result.items:
                    table.add_row(
                        f"[bold cyan]{user.login}[/bold cyan]",
                        user.name or "[dim]No name[/dim]",
                        user.company or "[dim]No company[/dim]",
                        user.location or "[dim]No location[/dim]",
                        str(user.followers or 0),
                        str(user.public_repos or 0),
                    )

                console.print(table)
                console.print(f"\n[dim]Total results: {result.total_count}[/dim]")
            else:
                output_data = {
                    "total_count": result.total_count,
                    "incomplete_results": result.incomplete_results,
                    "items": [user.model_dump() for user in result.items],
                }

                if output:
                    formatted_output = format_json(output_data)
                    with open(output, "w") as f:
                        f.write(formatted_output)
                    console.print(f"[green]Results written to {output}[/green]")
                else:
                    console.print(format_json(output_data))

    try:
        asyncio.run(_search_users())
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
