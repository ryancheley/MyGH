"""Pydantic models for GitHub API responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GitHubUser(BaseModel):
    """GitHub user model."""

    id: int
    login: str
    name: str | None = None
    email: str | None = None
    bio: str | None = None
    company: str | None = None
    location: str | None = None
    blog: str | None = None
    public_repos: int | None = Field(default=None, alias="public_repos")
    public_gists: int | None = Field(default=None, alias="public_gists")
    followers: int | None = None
    following: int | None = None
    created_at: datetime | None = Field(default=None, alias="created_at")
    updated_at: datetime | None = Field(default=None, alias="updated_at")
    avatar_url: str = Field(alias="avatar_url")
    html_url: str = Field(alias="html_url")

    model_config = ConfigDict(populate_by_name=True)


class GitHubRepo(BaseModel):
    """GitHub repository model."""

    id: int
    name: str
    full_name: str = Field(alias="full_name")
    description: str | None = None
    private: bool
    fork: bool
    language: str | None = None
    stargazers_count: int = Field(alias="stargazers_count")
    watchers_count: int = Field(alias="watchers_count")
    forks_count: int = Field(alias="forks_count")
    open_issues_count: int = Field(alias="open_issues_count")
    size: int
    default_branch: str = Field(alias="default_branch")
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")
    pushed_at: datetime | None = Field(alias="pushed_at", default=None)
    html_url: str = Field(alias="html_url")
    clone_url: str = Field(alias="clone_url")
    ssh_url: str = Field(alias="ssh_url")
    owner: GitHubUser

    model_config = ConfigDict(populate_by_name=True)


class GitHubGist(BaseModel):
    """GitHub gist model."""

    id: str
    description: str | None = None
    public: bool
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")
    html_url: str = Field(alias="html_url")
    files: dict[str, Any]
    owner: GitHubUser

    model_config = ConfigDict(populate_by_name=True)


class GitHubIssue(BaseModel):
    """GitHub issue model."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str
    user: GitHubUser
    assignee: GitHubUser | None = None
    assignees: list[GitHubUser] = []
    labels: list[dict[str, Any]] = []
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")
    closed_at: datetime | None = Field(alias="closed_at", default=None)
    html_url: str = Field(alias="html_url")

    model_config = ConfigDict(populate_by_name=True)


class GitHubBranch(BaseModel):
    """GitHub branch reference model."""

    label: str
    ref: str
    sha: str
    user: GitHubUser
    repo: "GitHubRepo"

    model_config = ConfigDict(populate_by_name=True)


class GitHubPullRequest(BaseModel):
    """GitHub pull request model."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str
    user: GitHubUser
    assignee: GitHubUser | None = None
    assignees: list[GitHubUser] = []
    labels: list[dict[str, Any]] = []
    head: GitHubBranch
    base: GitHubBranch
    draft: bool = False
    merged: bool = False
    mergeable: bool | None = None
    merged_at: datetime | None = Field(alias="merged_at", default=None)
    merged_by: GitHubUser | None = Field(alias="merged_by", default=None)
    comments: int = 0
    commits: int = 0
    additions: int = 0
    deletions: int = 0
    changed_files: int = Field(alias="changed_files", default=0)
    created_at: datetime = Field(alias="created_at")
    updated_at: datetime = Field(alias="updated_at")
    closed_at: datetime | None = Field(alias="closed_at", default=None)
    html_url: str = Field(alias="html_url")
    diff_url: str = Field(alias="diff_url")
    patch_url: str = Field(alias="patch_url")

    model_config = ConfigDict(populate_by_name=True)


class RateLimit(BaseModel):
    """GitHub API rate limit information."""

    limit: int
    remaining: int
    reset: datetime
    used: int


class SearchResult(BaseModel):
    """Base model for search results."""

    total_count: int = Field(alias="total_count")
    incomplete_results: bool = Field(alias="incomplete_results")

    model_config = ConfigDict(populate_by_name=True)


class RepoSearchResult(SearchResult):
    """Repository search result model."""

    items: list[GitHubRepo]


class UserSearchResult(SearchResult):
    """User search result model."""

    items: list[GitHubUser]
