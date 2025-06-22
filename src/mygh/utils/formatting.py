"""Output formatting utilities."""

import json
from datetime import datetime, timezone
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.text import Text

from ..api.models import GitHubGist, GitHubIssue, GitHubRepo, GitHubUser

console = Console()


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_days_since_commit(pushed_at: datetime | None) -> str:
    """Calculate days since last commit."""
    if pushed_at is None:
        return "N/A"

    now = datetime.now(timezone.utc)
    # Ensure pushed_at is timezone-aware
    if pushed_at.tzinfo is None:
        pushed_at = pushed_at.replace(tzinfo=timezone.utc)

    delta = now - pushed_at
    days = delta.days

    if days == 0:
        return "Today"
    elif days == 1:
        return "1 day"
    else:
        return f"{days} days"


def get_commit_age_style(pushed_at: datetime | None) -> Text:
    """Get styled text for commit age with color coding."""
    if pushed_at is None:
        return Text("N/A", style="dim")

    now = datetime.now(timezone.utc)
    # Ensure pushed_at is timezone-aware
    if pushed_at.tzinfo is None:
        pushed_at = pushed_at.replace(tzinfo=timezone.utc)

    delta = now - pushed_at
    days = delta.days

    if days == 0:
        return Text("Today", style="green")
    elif days == 1:
        return Text("1 day", style="green")
    elif days <= 7:
        return Text(f"{days} days", style="yellow")
    elif days <= 30:
        return Text(f"{days} days", style="orange3")
    elif days <= 365:
        return Text(f"{days} days", style="red")
    else:
        return Text(f"{days} days", style="dim red")


def format_user_table(users: list[GitHubUser]) -> Table:
    """Format users as a rich table."""
    table = Table(title="GitHub Users")
    table.add_column("Login", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Company", style="green")
    table.add_column("Location", style="yellow")
    table.add_column("Public Repos", justify="right", style="blue")
    table.add_column("Followers", justify="right", style="red")

    for user in users:
        table.add_row(
            user.login,
            user.name or "",
            user.company or "",
            user.location or "",
            str(user.public_repos) if user.public_repos is not None else "",
            str(user.followers) if user.followers is not None else "",
        )

    return table


def format_repo_table(repos: list[GitHubRepo]) -> Table:
    """Format repositories as a rich table."""
    table = Table(title="GitHub Repositories")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white", max_width=50)
    table.add_column("Language", style="magenta")
    table.add_column("Stars", justify="right", style="yellow")
    table.add_column("Forks", justify="right", style="green")
    table.add_column("Updated", style="blue")

    for repo in repos:
        description = repo.description or ""
        if len(description) > 47:
            description = description[:47] + "..."

        table.add_row(
            repo.name,
            description,
            repo.language or "",
            str(repo.stargazers_count),
            str(repo.forks_count),
            format_datetime(repo.updated_at),
        )

    return table


def format_starred_repo_table(repos: list[GitHubRepo]) -> Table:
    """Format starred repositories with owner and URL information."""
    table = Table(title="Starred GitHub Repositories")
    table.add_column("Owner/Name", style="cyan")
    table.add_column("Description", style="white", max_width=35)
    table.add_column("Language", style="magenta")
    table.add_column("Stars", justify="right", style="yellow")
    table.add_column("Last Commit", justify="right", style="red")
    table.add_column("URL", style="blue", max_width=25)

    for repo in repos:
        description = repo.description or ""
        if len(description) > 32:
            description = description[:32] + "..."

        # Format the full name as owner/repo
        full_name = f"{repo.owner.login}/{repo.name}"

        # Truncate URL for display
        url = repo.html_url
        if len(url) > 22:
            url = url[:22] + "..."

        # Get styled commit age
        commit_age_text = get_commit_age_style(repo.pushed_at)

        table.add_row(
            full_name,
            description,
            repo.language or "",
            str(repo.stargazers_count),
            commit_age_text,
            url,
        )

    return table


def format_gist_table(gists: list[GitHubGist]) -> Table:
    """Format gists as a rich table."""
    table = Table(title="GitHub Gists")
    table.add_column("ID", style="cyan")
    table.add_column("Description", style="white", max_width=50)
    table.add_column("Files", justify="right", style="magenta")
    table.add_column("Public", style="green")
    table.add_column("Created", style="blue")

    for gist in gists:
        description = gist.description or ""
        if len(description) > 47:
            description = description[:47] + "..."

        table.add_row(
            gist.id[:8] + "...",
            description,
            str(len(gist.files)),
            "Yes" if gist.public else "No",
            format_datetime(gist.created_at),
        )

    return table


def format_issue_table(issues: list[GitHubIssue]) -> Table:
    """Format issues as a rich table."""
    table = Table(title="GitHub Issues")
    table.add_column("Number", justify="right", style="cyan")
    table.add_column("Title", style="white", max_width=50)
    table.add_column("State", style="magenta")
    table.add_column("Author", style="green")
    table.add_column("Created", style="blue")

    for issue in issues:
        title = issue.title
        if len(title) > 47:
            title = title[:47] + "..."

        state_color = "green" if issue.state == "open" else "red"

        table.add_row(
            str(issue.number),
            title,
            Text(issue.state.upper(), style=state_color),
            issue.user.login,
            format_datetime(issue.created_at),
        )

    return table


def format_user_info(user: GitHubUser) -> None:
    """Format and display user information."""
    console.print(f"\n[bold cyan]{user.name or user.login}[/bold cyan] (@{user.login})")

    if user.bio:
        console.print(f"[white]{user.bio}[/white]")

    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")

    if user.company:
        info_table.add_row("Company:", user.company)
    if user.location:
        info_table.add_row("Location:", user.location)
    if user.email:
        info_table.add_row("Email:", user.email)
    if user.blog:
        info_table.add_row("Blog:", user.blog)

    if user.public_repos is not None:
        info_table.add_row("Public Repos:", str(user.public_repos))
    if user.public_gists is not None:
        info_table.add_row("Public Gists:", str(user.public_gists))
    if user.followers is not None:
        info_table.add_row("Followers:", str(user.followers))
    if user.following is not None:
        info_table.add_row("Following:", str(user.following))
    if user.created_at is not None:
        info_table.add_row("Joined:", format_datetime(user.created_at))
    info_table.add_row("Profile:", user.html_url)

    console.print(info_table)


def format_json(data: Any) -> str:
    """Format data as JSON."""
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    elif hasattr(data, "dict"):  # Fallback for older pydantic
        data = data.dict()
    elif isinstance(data, list) and data:
        if hasattr(data[0], "model_dump"):
            data = [item.model_dump() for item in data]
        elif hasattr(data[0], "dict"):  # Fallback for older pydantic
            data = [item.dict() for item in data]

    return json.dumps(data, indent=2, default=str)


def format_csv_repos(repos: list[GitHubRepo]) -> str:
    """Format repositories as CSV."""
    lines = ["name,description,language,stars,forks,updated_at,html_url"]

    for repo in repos:
        description = (repo.description or "").replace('"', '""').replace("\n", " ")
        lines.append(
            f'"{repo.name}","{description}","{repo.language or ""}",'
            f"{repo.stargazers_count},{repo.forks_count},"
            f'"{format_datetime(repo.updated_at)}","{repo.html_url}"'
        )

    return "\n".join(lines)


def format_csv_starred_repos(repos: list[GitHubRepo]) -> str:
    """Format starred repositories as CSV with owner information."""
    lines = [
        "owner,name,full_name,description,language,stars,"
        "days_since_last_commit,pushed_at,html_url"
    ]

    for repo in repos:
        description = (repo.description or "").replace('"', '""').replace("\n", " ")
        days_since_commit = calculate_days_since_commit(repo.pushed_at)
        pushed_at_str = repo.pushed_at.isoformat() if repo.pushed_at else ""

        lines.append(
            f'"{repo.owner.login}","{repo.name}","{repo.full_name}",'
            f'"{description}","{repo.language or ""}",'
            f'{repo.stargazers_count},"{days_since_commit}","{pushed_at_str}","{repo.html_url}"'
        )

    return "\n".join(lines)


def print_output(
    data: Any,
    format_type: str = "table",
    output_file: str | None = None,
    is_starred: bool = False,
) -> None:
    """Print or save formatted output.

    Args:
        data: Data to format and output
        format_type: Output format (table, json, csv)
        output_file: Optional file to save output to
        is_starred: Whether this is starred repositories (for special formatting)
    """
    if format_type == "json":
        output = format_json(data)
    elif (
        format_type == "csv"
        and isinstance(data, list)
        and data
        and isinstance(data[0], GitHubRepo)
    ):
        if is_starred:
            output = format_csv_starred_repos(data)
        else:
            output = format_csv_repos(data)
    else:
        # Default to table format
        if isinstance(data, GitHubUser):
            format_user_info(data)
            return
        elif isinstance(data, list) and data:
            if isinstance(data[0], GitHubRepo):
                if is_starred:
                    table = format_starred_repo_table(data)
                else:
                    table = format_repo_table(data)
            elif isinstance(data[0], GitHubGist):
                table = format_gist_table(data)
            elif isinstance(data[0], GitHubIssue):
                table = format_issue_table(data)
            elif isinstance(data[0], GitHubUser):
                table = format_user_table(data)
            else:
                console.print(data)
                return

            if output_file:
                console.print(
                    "Table format cannot be saved to file. Use --format json or csv."
                )
                return

            console.print(table)
            return
        else:
            console.print("No data to display")
            return

    if output_file:
        with open(output_file, "w") as f:
            f.write(output)
        console.print(f"Output saved to {output_file}")
    else:
        console.print(output)
