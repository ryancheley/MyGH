"""Repository management CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt

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
    username: str | None = typer.Argument(None, help="GitHub username (defaults to authenticated user)"),
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
    limit: int = typer.Option(30, "--limit", help="Maximum number of repositories to fetch"),
    format_type: str = typer.Option("table", "--format", "-f", help="Output format (table, json, csv)"),
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
    format_type: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
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
    state: str = typer.Option("open", "--state", "-s", help="Issue state (open, closed, all)"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="Filter by assignee (@me for yourself)"),
    labels: str | None = typer.Option(None, "--labels", "-l", help="Filter by labels (comma-separated)"),
    limit: int = typer.Option(30, "--limit", help="Maximum number of issues to fetch"),
    format_type: str = typer.Option("table", "--format", "-f", help="Output format (table, json)"),
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


@repos_app.command("create")
@handle_exceptions  # type: ignore[misc]
async def create_repo(
    name: str = typer.Argument(help="Repository name"),
    description: str | None = typer.Option(None, "--description", "-d", help="Repository description"),
    private: bool = typer.Option(False, "--private", help="Make repository private"),
    has_issues: bool = typer.Option(True, "--issues/--no-issues", help="Enable issues"),
    has_wiki: bool = typer.Option(True, "--wiki/--no-wiki", help="Enable wiki"),
    has_projects: bool = typer.Option(True, "--projects/--no-projects", help="Enable projects"),
    auto_init: bool = typer.Option(True, "--init/--no-init", help="Initialize with README"),
    gitignore_template: str | None = typer.Option(None, "--gitignore", help="Gitignore template"),
    license_template: str | None = typer.Option(None, "--license", help="License template"),
    allow_squash_merge: bool = typer.Option(True, "--squash/--no-squash", help="Allow squash merge"),
    allow_merge_commit: bool = typer.Option(True, "--merge/--no-merge", help="Allow merge commit"),
    allow_rebase_merge: bool = typer.Option(True, "--rebase/--no-rebase", help="Allow rebase merge"),
    delete_branch_on_merge: bool = typer.Option(True, "--delete-branch/--keep-branch", help="Delete branch on merge"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive repository creation"),
) -> None:
    """Create a new repository."""
    config = config_manager.get_config()

    # Interactive mode
    if interactive:
        console.print("[bold cyan]🚀 Interactive Repository Creation[/bold cyan]\n")

        name = Prompt.ask("Repository name", default=name)
        description = Prompt.ask("Description", default=description or "")
        private = Confirm.ask("Make repository private?", default=private)
        has_issues = Confirm.ask("Enable issues?", default=has_issues)
        has_wiki = Confirm.ask("Enable wiki?", default=has_wiki)
        has_projects = Confirm.ask("Enable projects?", default=has_projects)
        auto_init = Confirm.ask("Initialize with README?", default=auto_init)

        if auto_init:
            gitignore_template = Prompt.ask("Gitignore template (optional)", default=gitignore_template or "")
            license_template = Prompt.ask("License template (optional)", default=license_template or "")

        console.print(f"\n[yellow]Creating repository '{name}'...[/yellow]")

    client = GitHubClient(token=config.github_token)
    try:
        repo_data = {
            "name": name,
            "description": description or "",
            "private": private,
            "has_issues": has_issues,
            "has_wiki": has_wiki,
            "has_projects": has_projects,
            "auto_init": auto_init,
            "allow_squash_merge": allow_squash_merge,
            "allow_merge_commit": allow_merge_commit,
            "allow_rebase_merge": allow_rebase_merge,
            "delete_branch_on_merge": delete_branch_on_merge,
        }

        if gitignore_template:
            repo_data["gitignore_template"] = gitignore_template
        if license_template:
            repo_data["license_template"] = license_template

        repo = await client.create_repo(repo_data)

        console.print(f"[green]✅ Repository '{repo.full_name}' created successfully![/green]")
        console.print(f"[blue]📍 URL: {repo.html_url}[/blue]")
        console.print(f"[blue]🔗 Clone URL: {repo.clone_url}[/blue]")

    finally:
        await client.close()


@repos_app.command("update")
@handle_exceptions  # type: ignore[misc]
async def update_repo(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    description: str | None = typer.Option(None, "--description", "-d", help="Update description"),
    homepage: str | None = typer.Option(None, "--homepage", help="Update homepage URL"),
    private: bool | None = typer.Option(None, "--private/--public", help="Change visibility"),
    has_issues: bool | None = typer.Option(None, "--issues/--no-issues", help="Enable/disable issues"),
    has_wiki: bool | None = typer.Option(None, "--wiki/--no-wiki", help="Enable/disable wiki"),
    has_projects: bool | None = typer.Option(None, "--projects/--no-projects", help="Enable/disable projects"),
    allow_squash_merge: bool | None = typer.Option(None, "--squash/--no-squash", help="Allow squash merge"),
    allow_merge_commit: bool | None = typer.Option(None, "--merge/--no-merge", help="Allow merge commit"),
    allow_rebase_merge: bool | None = typer.Option(None, "--rebase/--no-rebase", help="Allow rebase merge"),
    delete_branch_on_merge: bool | None = typer.Option(
        None, "--delete-branch/--keep-branch", help="Delete branch on merge"
    ),
    archived: bool | None = typer.Option(None, "--archive/--unarchive", help="Archive repository"),
) -> None:
    """Update repository settings."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        # Build update data with only provided values
        update_data = {}
        if description is not None:
            update_data["description"] = description
        if homepage is not None:
            update_data["homepage"] = homepage
        if private is not None:
            update_data["private"] = private
        if has_issues is not None:
            update_data["has_issues"] = has_issues
        if has_wiki is not None:
            update_data["has_wiki"] = has_wiki
        if has_projects is not None:
            update_data["has_projects"] = has_projects
        if allow_squash_merge is not None:
            update_data["allow_squash_merge"] = allow_squash_merge
        if allow_merge_commit is not None:
            update_data["allow_merge_commit"] = allow_merge_commit
        if allow_rebase_merge is not None:
            update_data["allow_rebase_merge"] = allow_rebase_merge
        if delete_branch_on_merge is not None:
            update_data["delete_branch_on_merge"] = delete_branch_on_merge
        if archived is not None:
            update_data["archived"] = archived

        if not update_data:
            console.print("[yellow]No updates specified[/yellow]")
            return

        updated_repo = await client.update_repo(owner, repo, update_data)

        console.print(f"[green]✅ Repository '{updated_repo.full_name}' updated successfully![/green]")
        console.print(f"[blue]📍 URL: {updated_repo.html_url}[/blue]")

    finally:
        await client.close()


@repos_app.command("delete")
@handle_exceptions  # type: ignore[misc]
async def delete_repo(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a repository."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    # Confirmation
    if not force:
        console.print(f"[red]⚠️  This will permanently delete the repository '{repo_name}'![/red]")
        console.print("[red]This action cannot be undone![/red]")

        if not Confirm.ask("Are you sure you want to delete this repository?"):
            console.print("[yellow]Repository deletion cancelled[/yellow]")
            return

        # Double confirmation for safety
        confirmation_text = Prompt.ask(f"Type the repository name '{repo_name}' to confirm deletion")
        if confirmation_text != repo_name:
            console.print("[red]Repository name doesn't match. Deletion cancelled.[/red]")
            return

    client = GitHubClient(token=config.github_token)
    try:
        await client.delete_repo(owner, repo)
        console.print(f"[green]✅ Repository '{repo_name}' deleted successfully[/green]")

    finally:
        await client.close()


@repos_app.command("fork")
@handle_exceptions  # type: ignore[misc]
async def fork_repo(
    repo_name: str = typer.Argument(help="Repository name (owner/repo format)"),
    organization: str | None = typer.Option(None, "--org", help="Fork to organization"),
) -> None:
    """Fork a repository."""
    if "/" not in repo_name:
        console.print("[red]Repository name must be in 'owner/repo' format[/red]")
        raise typer.Exit(1)

    owner, repo = repo_name.split("/", 1)
    config = config_manager.get_config()

    client = GitHubClient(token=config.github_token)
    try:
        fork_data = {}
        if organization:
            fork_data["organization"] = organization

        forked_repo = await client.fork_repo(owner, repo, fork_data)

        console.print(f"[green]✅ Repository '{repo_name}' forked successfully![/green]")
        console.print(f"[blue]📍 Fork URL: {forked_repo.html_url}[/blue]")
        console.print(f"[blue]🔗 Clone URL: {forked_repo.clone_url}[/blue]")

    finally:
        await client.close()
