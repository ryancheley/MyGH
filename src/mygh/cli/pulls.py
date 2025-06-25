"""Pull request management CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..api.client import GitHubClient
from ..api.models import GitHubPullRequest
from ..exceptions import APIError, AuthenticationError, MyGHException
from ..utils.config import ConfigManager
from ..utils.formatting import format_datetime, print_output

console = Console()
pulls_app = typer.Typer(help="Pull request management commands")
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


@pulls_app.command("list")
@handle_exceptions  # type: ignore[misc]
async def list_pulls(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    state: str = typer.Option(
        "open", "--state", "-s", help="Pull request state (open, closed, all)"
    ),
    base: str | None = typer.Option(None, "--base", help="Filter by base branch"),
    head: str | None = typer.Option(None, "--head", help="Filter by head branch"),
    sort: str = typer.Option(
        "created", "--sort", help="Sort order (created, updated, popularity)"
    ),
    direction: str = typer.Option(
        "desc", "--direction", help="Sort direction (asc, desc)"
    ),
    limit: int = typer.Option(30, "--limit", help="Maximum number of PRs to fetch"),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json)"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """List pull requests."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        pulls: list[GitHubPullRequest] = []
        page = 1
        per_page = min(100, limit)

        while len(pulls) < limit:
            batch = await client.get_pull_requests(
                owner=owner,
                repo=repo,
                state=state,
                base=base,
                head=head,
                sort=sort,
                direction=direction,
                per_page=per_page,
                page=page,
            )

            if not batch:
                break

            pulls.extend(batch)

            if len(batch) < per_page:
                break

            page += 1

        # Trim to requested limit
        pulls = pulls[:limit]

        if not pulls:
            console.print("[yellow]No pull requests found[/yellow]")
            return

        print_output(pulls, format_type, output)
    finally:
        await client.close()


@pulls_app.command("create")
@handle_exceptions  # type: ignore[misc]
async def create_pull(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    title: str = typer.Option(..., "--title", "-t", help="Pull request title"),
    head: str = typer.Option(..., "--head", help="Head branch (source)"),
    base: str = typer.Option("main", "--base", help="Base branch (target)"),
    body: str | None = typer.Option(None, "--body", "-b", help="Pull request body"),
    draft: bool = typer.Option(False, "--draft", help="Create as draft"),
    maintainer_can_modify: bool = typer.Option(
        True, "--maintainer-modify/--no-maintainer-modify", help="Allow maintainer modifications"
    ),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive PR creation"),
) -> None:
    """Create a new pull request."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    # Interactive mode
    if interactive:
        console.print("[bold cyan]🚀 Interactive Pull Request Creation[/bold cyan]\n")

        title = Prompt.ask("Pull request title", default=title)
        head = Prompt.ask("Head branch (source)", default=head)
        base = Prompt.ask("Base branch (target)", default=base)
        body = Prompt.ask("Pull request body (optional)", default=body or "")
        draft = Confirm.ask("Create as draft?", default=draft)

        console.print(f"\n[yellow]Creating pull request '{title}'...[/yellow]")

    client = GitHubClient(token=config.github_token)
    try:
        pr_data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body or "",
            "draft": draft,
            "maintainer_can_modify": maintainer_can_modify,
        }

        pr = await client.create_pull_request(owner, repo, pr_data)

        console.print(f"[green]✅ Pull request #{pr.number} created successfully![/green]")
        console.print(f"[blue]📍 URL: {pr.html_url}[/blue]")
        console.print(f"[blue]🎯 {head} → {base}[/blue]")

    finally:
        await client.close()


@pulls_app.command("update")
@handle_exceptions  # type: ignore[misc]
async def update_pull(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    pr_number: int = typer.Argument(help="Pull request number"),
    title: str | None = typer.Option(None, "--title", "-t", help="Update title"),
    body: str | None = typer.Option(None, "--body", "-b", help="Update body"),
    state: str | None = typer.Option(None, "--state", help="Update state (open, closed)"),
    base: str | None = typer.Option(None, "--base", help="Update base branch"),
) -> None:
    """Update a pull request."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        # Build update data with only provided values
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if body is not None:
            update_data["body"] = body
        if state is not None:
            update_data["state"] = state
        if base is not None:
            update_data["base"] = base

        if not update_data:
            console.print("[yellow]No updates specified[/yellow]")
            return

        updated_pr = await client.update_pull_request(owner, repo, pr_number, update_data)

        console.print(f"[green]✅ Pull request #{updated_pr.number} updated successfully![/green]")
        console.print(f"[blue]📍 URL: {updated_pr.html_url}[/blue]")

    finally:
        await client.close()


@pulls_app.command("merge")
@handle_exceptions  # type: ignore[misc]
async def merge_pull(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    pr_number: int = typer.Argument(help="Pull request number"),
    commit_title: str | None = typer.Option(None, "--title", help="Merge commit title"),
    commit_message: str | None = typer.Option(None, "--message", help="Merge commit message"),
    merge_method: str = typer.Option(
        "merge", "--method", help="Merge method (merge, squash, rebase)"
    ),
    delete_branch: bool = typer.Option(
        False, "--delete-branch", help="Delete head branch after merge"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Merge a pull request."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    # Confirmation
    if not force:
        if not Confirm.ask(f"Are you sure you want to merge PR #{pr_number}?"):
            console.print("[yellow]Merge cancelled[/yellow]")
            return

    client = GitHubClient(token=config.github_token)
    try:
        merge_data = {
            "merge_method": merge_method,
        }
        if commit_title:
            merge_data["commit_title"] = commit_title
        if commit_message:
            merge_data["commit_message"] = commit_message

        result = await client.merge_pull_request(owner, repo, pr_number, merge_data)

        console.print(f"[green]✅ Pull request #{pr_number} merged successfully![/green]")
        console.print(f"[blue]📍 Merge commit: {result.get('sha', 'N/A')}[/blue]")

        if delete_branch:
            # Get PR details to find head branch
            pr = await client.get_pull_request(owner, repo, pr_number)
            if pr.head.ref:
                try:
                    await client.delete_branch(owner, repo, pr.head.ref)
                    console.print(f"[green]🗑️  Branch '{pr.head.ref}' deleted[/green]")
                except Exception as e:
                    console.print(f"[yellow]⚠️  Could not delete branch: {e}[/yellow]")

    finally:
        await client.close()


@pulls_app.command("close")
@handle_exceptions  # type: ignore[misc]
async def close_pull(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    pr_number: int = typer.Argument(help="Pull request number"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Close a pull request without merging."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    # Confirmation
    if not force:
        if not Confirm.ask(f"Are you sure you want to close PR #{pr_number} without merging?"):
            console.print("[yellow]Close cancelled[/yellow]")
            return

    client = GitHubClient(token=config.github_token)
    try:
        updated_pr = await client.update_pull_request(
            owner, repo, pr_number, {"state": "closed"}
        )

        console.print(f"[green]✅ Pull request #{updated_pr.number} closed successfully![/green]")
        console.print(f"[blue]📍 URL: {updated_pr.html_url}[/blue]")

    finally:
        await client.close()


@pulls_app.command("show")
@handle_exceptions  # type: ignore[misc]
async def show_pull(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    pr_number: int = typer.Argument(help="Pull request number"),
    show_diff: bool = typer.Option(False, "--diff", help="Show diff"),
    format_type: str = typer.Option(
        "table", "--format", "-f", help="Output format (table, json)"
    ),
) -> None:
    """Show pull request details."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        pr = await client.get_pull_request(owner, repo, pr_number)

        if format_type == "json":
            print_output(pr, format_type)
        else:
            # Custom display for PR details
            console.print(f"\n[bold cyan]Pull Request #{pr.number}[/bold cyan]")
            console.print(f"[bold]{pr.title}[/bold]")

            if pr.body:
                console.print(f"\n{pr.body}")

            # PR info table
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Field", style="bold")
            info_table.add_column("Value")

            state_color = "green" if pr.state == "open" else "red"
            info_table.add_row("State", f"[{state_color}]{pr.state.upper()}[/{state_color}]")
            info_table.add_row("Author", pr.user.login)
            info_table.add_row("Head", f"{pr.head.label} ({pr.head.sha[:8]})")
            info_table.add_row("Base", f"{pr.base.label} ({pr.base.sha[:8]})")
            info_table.add_row("Created", format_datetime(pr.created_at))
            info_table.add_row("Updated", format_datetime(pr.updated_at))

            if pr.merged_at:
                info_table.add_row("Merged", format_datetime(pr.merged_at))

            info_table.add_row("Mergeable", "Yes" if pr.mergeable else "No")
            info_table.add_row("Comments", str(pr.comments))
            info_table.add_row("Commits", str(pr.commits))
            info_table.add_row("Additions", f"[green]+{pr.additions}[/green]")
            info_table.add_row("Deletions", f"[red]-{pr.deletions}[/red]")
            info_table.add_row("Changed Files", str(pr.changed_files))
            info_table.add_row("URL", pr.html_url)

            console.print(info_table)

        if show_diff:
            console.print("\n[bold]Diff:[/bold]")
            diff = await client.get_pull_request_diff(owner, repo, pr_number)
            console.print(diff)

    finally:
        await client.close()


if __name__ == "__main__":
    pulls_app()
