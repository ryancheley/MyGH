"""GitHub Actions integration CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..api.client import GitHubClient
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager

console = Console()
actions_app = typer.Typer(help="GitHub Actions integration commands")
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


@actions_app.command("workflows")
@handle_exceptions  # type: ignore[misc]
async def list_workflows(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    format_type: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
) -> None:
    """List repository workflows."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        workflows = await client.get_workflows(owner, repo)

        if not workflows:
            console.print("[yellow]No workflows found[/yellow]")
            return

        if format_type == "json":
            import json
            console.print(json.dumps([w.__dict__ for w in workflows], indent=2, default=str))
        else:
            table = Table(title=f"Workflows for {repo_name}")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("State", style="yellow")
            table.add_column("Path", style="blue")

            for workflow in workflows:
                table.add_row(
                    str(workflow.get("id", "N/A")),
                    workflow.get("name", "N/A"),
                    workflow.get("state", "N/A"),
                    workflow.get("path", "N/A"),
                )

            console.print(table)

    finally:
        await client.close()


@actions_app.command("runs")
@handle_exceptions  # type: ignore[misc]
async def list_runs(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    workflow_id: str | None = typer.Option(None, "--workflow", help="Filter by workflow ID"),
    status: str | None = typer.Option(None, "--status", help="Filter by status"),
    limit: int = typer.Option(20, "--limit", help="Maximum number of runs"),
) -> None:
    """List workflow runs."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        runs = await client.get_workflow_runs(owner, repo, workflow_id, status, limit)

        if not runs:
            console.print("[yellow]No workflow runs found[/yellow]")
            return

        table = Table(title=f"Workflow Runs for {repo_name}")
        table.add_column("ID", style="cyan")
        table.add_column("Workflow", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Conclusion", style="red")
        table.add_column("Branch", style="blue")
        table.add_column("Started", style="magenta")

        for run in runs:
            status_color = "green" if run.get("status") == "completed" else "yellow"
            conclusion_color = "green" if run.get("conclusion") == "success" else "red"

            table.add_row(
                str(run.get("id", "N/A")),
                run.get("name", "N/A"),
                f"[{status_color}]{run.get('status', 'N/A')}[/{status_color}]",
                f"[{conclusion_color}]{run.get('conclusion', 'N/A')}[/{conclusion_color}]",
                run.get("head_branch", "N/A"),
                run.get("created_at", "N/A"),
            )

        console.print(table)

    finally:
        await client.close()


if __name__ == "__main__":
    actions_app()
