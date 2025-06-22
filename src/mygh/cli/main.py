"""Main CLI entry point for MyGH."""

import asyncio

import typer
from rich.console import Console

from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager
from .repos import repos_app
from .user import user_app

console = Console()
app = typer.Typer(
    name="mygh",
    help="A comprehensive GitHub CLI tool",
    rich_markup_mode="rich",
)

# Add sub-commands
app.add_typer(user_app, name="user", help="User-related commands")
app.add_typer(repos_app, name="repos", help="Repository management commands")

# Global configuration manager
config_manager = ConfigManager()


@app.command()
def config(
    action: str = typer.Argument(help="Action to perform (set, get, list)"),
    key: str | None = typer.Argument(None, help="Configuration key"),
    value: str | None = typer.Argument(None, help="Configuration value"),
) -> None:
    """Manage MyGH configuration."""
    try:
        if action == "list":
            config_data = config_manager.list_config()
            console.print("\n[bold]Current Configuration:[/bold]")
            for k, v in config_data.items():
                console.print(f"  [cyan]{k}[/cyan]: {v}")

        elif action == "get":
            if not key:
                raise typer.BadParameter("Key is required for 'get' action")
            config_data = config_manager.list_config()
            if key in config_data:
                console.print(f"{key}: {config_data[key]}")
            else:
                console.print(f"[red]Configuration key '{key}' not found[/red]")
                raise typer.Exit(1) from None

        elif action == "set":
            if not key or value is None:
                raise typer.BadParameter(
                    "Both key and value are required for 'set' action"
                )
            config_manager.set_config_value(key, value)
            console.print(f"[green]Set {key} = {value}[/green]")

        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            console.print("Available actions: list, get, set")
            raise typer.Exit(1) from None

    except ValueError as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        raise typer.Exit(1) from None


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None, "--version", "-v", help="Show version and exit"
    ),
) -> None:
    """MyGH - A comprehensive GitHub CLI tool."""
    if version:
        from .. import __version__

        console.print(f"mygh version {__version__}")
        raise typer.Exit()


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


if __name__ == "__main__":
    app()
