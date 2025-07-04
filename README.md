# MyGH - A Comprehensive GitHub CLI Tool

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Built with uv](https://img.shields.io/badge/built%20with-uv-green)](https://github.com/astral-sh/uv)
[![Test Coverage](https://img.shields.io/badge/coverage-97%25-brightgreen)](https://github.com/ryancheley/MyGH)
[![Code Quality](https://img.shields.io/badge/code%20quality-A+-brightgreen)](https://github.com/astral-sh/ruff)

MyGH is a modern, feature-rich command-line interface for GitHub that provides comprehensive user insights and repository management capabilities. Built with Python, Typer, and the GitHub REST API, it offers a beautiful and intuitive developer experience.

## ✨ Features

### 🔍 User Information
- **User Profiles**: Get detailed information about any GitHub user
- **Starred Repositories**: List and filter starred repositories by language with commit age tracking
- **Gists Management**: Browse and manage user gists

### 📦 Repository Management
- **Repository Listing**: List repositories with flexible filtering and sorting
- **Repository Details**: Get comprehensive information about specific repositories
- **Issue Tracking**: Browse repository issues with advanced filtering
- **Repository Creation**: Create new repositories with full configuration options
- **Repository Updates**: Modify repository settings, visibility, and features
- **Repository Deletion**: Safely delete repositories with confirmation prompts
- **Repository Forking**: Fork repositories to your account or organizations

### 🔄 Pull Request Management
- **PR Listing**: List and filter pull requests by state, branch, and author
- **PR Creation**: Create pull requests with interactive prompts and draft support
- **PR Updates**: Modify titles, descriptions, and other PR attributes
- **PR Merging**: Merge pull requests with different strategies (merge, squash, rebase)
- **PR Details**: View comprehensive PR information with diffs and statistics

### 🚀 GitHub Actions Integration
- **Workflow Listing**: Browse repository workflows and their configurations
- **Workflow Runs**: Monitor workflow runs with status and conclusion filtering
- **Real-time Status**: Track CI/CD pipeline execution and results

### 🏢 Organization Management
- **Organization Listing**: View your organization memberships
- **Member Management**: List organization members with role filtering
- **Team Overview**: Browse organization teams and their descriptions

### 🔍 Advanced Search
- **Repository Search**: Find repositories using GitHub's powerful search syntax
- **User Search**: Discover users with advanced filtering and sorting
- **Search Operators**: Support for all GitHub search qualifiers and operators

### 🔔 Notification Management
- **Notification Listing**: View unread and participating notifications
- **Bulk Operations**: Mark notifications as read globally or per repository
- **Filtering Options**: Focus on relevant notifications with various filters

### 👥 Team Management
- **Team Listing**: Browse organization teams with member counts
- **Member Details**: View team membership and roles
- **Team Privacy**: Support for public and private team visibility

### 🖥️ Interactive Browser
- **Repository Browser**: Navigate repositories with keyboard shortcuts
- **Real-time Filtering**: Search and filter repositories interactively
- **Detailed Views**: Inspect repository details without leaving the terminal

### 🎨 Output Formats
- **Rich Tables**: Beautiful, colorized terminal output with commit age indicators (default)
- **JSON Export**: Machine-readable format for automation
- **CSV Export**: Data analysis-friendly format for repositories

### ⚙️ Configuration
- **Flexible Authentication**: Multiple authentication methods
- **Persistent Settings**: Save preferences with TOML configuration
- **Environment Variables**: Override settings with environment variables

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- GitHub account and access token

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ryancheley/MyGH.git
   cd MyGH
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync --dev
   ```

3. **Set up GitHub authentication:**
   
   **Option A: Environment Variable**
   ```bash
   export GITHUB_TOKEN="your_personal_access_token"
   ```
   
   **Option B: GitHub CLI Integration**
   ```bash
   gh auth login
   ```

4. **Test the installation:**
   ```bash
   uv run mygh --help
   ```

### Creating a GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `user`, `gist`
4. Copy the generated token
5. Set it as the `GITHUB_TOKEN` environment variable

## 📖 Usage Guide

### User Commands

#### Get User Information
```bash
# Get your own user information
uv run mygh user info

# Get information about a specific user
uv run mygh user info octocat

# Export as JSON
uv run mygh user info --format json --output user.json
```

#### List Starred Repositories
```bash
# List your starred repositories
uv run mygh user starred

# Filter by programming language
uv run mygh user starred --language python

# Limit results and export as CSV
uv run mygh user starred --limit 50 --format csv --output starred.csv

# List another user's starred repositories
uv run mygh user starred octocat --language javascript
```

#### Browse User Gists
```bash
# List your gists
uv run mygh user gists

# Show only public gists
uv run mygh user gists --public

# List another user's gists
uv run mygh user gists octocat --format json
```

### Repository Commands

#### List Repositories
```bash
# List your repositories
uv run mygh repos list

# Filter by type and sort
uv run mygh repos list --type public --sort updated

# List another user's repositories
uv run mygh repos list octocat --limit 20

# Export as CSV
uv run mygh repos list --format csv --output repos.csv
```

#### Get Repository Information
```bash
# Get detailed repository information
uv run mygh repos info octocat/Hello-World

# Export repository details as JSON
uv run mygh repos info microsoft/vscode --format json
```

#### Browse Repository Issues
```bash
# List open issues
uv run mygh repos issues octocat/Hello-World

# Filter by state and assignee
uv run mygh repos issues microsoft/vscode --state closed --assignee @me

# Filter by labels
uv run mygh repos issues facebook/react --labels "bug,help wanted"

# Export issues as JSON
uv run mygh repos issues vuejs/vue --format json --output issues.json
```

### Repository Management (Extended)

#### Create Repositories
```bash
# Create a new repository
uv run mygh repos create my-new-repo --description "My awesome project"

# Create with interactive prompts
uv run mygh repos create my-repo --interactive

# Create private repository with custom settings
uv run mygh repos create my-private-repo --private --no-wiki --no-projects
```

#### Update Repository Settings
```bash
# Update repository description
uv run mygh repos update myuser/my-repo --description "Updated description"

# Change repository visibility
uv run mygh repos update myuser/my-repo --private

# Enable/disable features
uv run mygh repos update myuser/my-repo --issues --no-wiki
```

#### Delete and Fork Repositories
```bash
# Delete a repository (with confirmation)
uv run mygh repos delete myuser/old-repo

# Fork a repository
uv run mygh repos fork microsoft/vscode

# Fork to an organization
uv run mygh repos fork microsoft/vscode --org myorg
```

### Pull Request Management

#### List Pull Requests
```bash
# List open pull requests
uv run mygh pulls list microsoft/vscode

# Filter by state and branch
uv run mygh pulls list microsoft/vscode --state closed --base main

# Sort by creation date
uv run mygh pulls list microsoft/vscode --sort created --direction asc
```

#### Create Pull Requests
```bash
# Create a new pull request
uv run mygh pulls create myuser/my-repo --title "Add new feature" --head feature-branch --base main

# Create with interactive prompts
uv run mygh pulls create myuser/my-repo --interactive

# Create as draft
uv run mygh pulls create myuser/my-repo --title "WIP: New feature" --head feature --draft
```

#### Manage Pull Requests
```bash
# Show pull request details
uv run mygh pulls show microsoft/vscode 123

# Show with diff
uv run mygh pulls show microsoft/vscode 123 --diff

# Update pull request
uv run mygh pulls update microsoft/vscode 123 --title "Updated title" --body "New description"

# Merge pull request
uv run mygh pulls merge microsoft/vscode 123 --method squash --delete-branch

# Close without merging
uv run mygh pulls close microsoft/vscode 123
```

### GitHub Actions Integration

#### List Workflows
```bash
# List repository workflows
uv run mygh actions workflows microsoft/vscode

# Export as JSON
uv run mygh actions workflows microsoft/vscode --format json
```

#### Monitor Workflow Runs
```bash
# List recent workflow runs
uv run mygh actions runs microsoft/vscode

# Filter by workflow and status
uv run mygh actions runs microsoft/vscode --workflow ci.yml --status failure

# Limit results
uv run mygh actions runs microsoft/vscode --limit 10
```

### Organization Management

#### List Organizations
```bash
# List your organizations
uv run mygh orgs list
```

#### Manage Organization Members
```bash
# List organization members
uv run mygh orgs members myorg

# Filter by role
uv run mygh orgs members myorg --role admin
```

### Advanced Search

#### Search Repositories
```bash
# Search repositories by keyword
uv run mygh search repos "machine learning"

# Search with filters and sorting
uv run mygh search repos "language:python stars:>1000" --sort stars --order desc

# Limit results
uv run mygh search repos "react" --limit 10
```

#### Search Users
```bash
# Search users
uv run mygh search users "location:London"

# Sort by followers
uv run mygh search users "repos:>50" --sort followers --order desc
```

### Notification Management

#### List Notifications
```bash
# List unread notifications
uv run mygh notifications list

# Include read notifications
uv run mygh notifications list --all

# Show only participating notifications
uv run mygh notifications list --participating
```

#### Mark as Read
```bash
# Mark all notifications as read
uv run mygh notifications mark-read

# Mark notifications for specific repository as read
uv run mygh notifications mark-read --repo microsoft/vscode
```

### Team Management

#### List Teams
```bash
# List organization teams
uv run mygh teams list myorg
```

#### Manage Team Members
```bash
# List team members
uv run mygh teams members myorg developers

# Show team member details
uv run mygh teams members myorg developers
```

### Interactive Repository Browser

#### Launch Browser
```bash
# Browse your repositories interactively
uv run mygh browse repos

# Browse another user's repositories
uv run mygh browse repos --user octocat

# Browse starred repositories only
uv run mygh browse starred

# Browse another user's starred repositories
uv run mygh browse starred --user octocat
```

**Browser Controls:**
- `Arrow keys`: Navigate through repositories
- `Enter`: Perform selected action
- `f`: Focus search input
- `Escape`: Clear search
- `r`: Refresh repository list
- `q` or `Ctrl+C`: Quit browser

**Features:**
- Real-time search and filtering
- Category filters (All, Starred, Owned, Forked, With Issues)
- Repository details sidebar
- Quick actions (star, fork, clone, open in browser)

### Configuration Management

#### List Current Configuration
```bash
uv run mygh config list
```

#### Set Configuration Values
```bash
# Set default output format
uv run mygh config set output-format json

# Set default results per page
uv run mygh config set default-per-page 50
```

#### Get Specific Configuration Value
```bash
uv run mygh config get output-format
```

## 🔧 Configuration

MyGH uses a TOML configuration file located at `~/.config/mygh/config.toml`. Here's an example:

```toml
output-format = "table"
default-per-page = 30
```

### Configuration Options

| Option | Description | Default | Environment Variable |
|--------|-------------|---------|---------------------|
| `output-format` | Default output format (table, json, csv) | `table` | `MYGH_OUTPUT_FORMAT` |
| `default-per-page` | Default number of results per page | `30` | `MYGH_DEFAULT_PER_PAGE` |
| `github-token` | GitHub personal access token | - | `GITHUB_TOKEN` |

### Environment Variables

Environment variables take precedence over configuration file settings:

- `GITHUB_TOKEN` or `GH_TOKEN`: GitHub authentication token
- `MYGH_OUTPUT_FORMAT`: Default output format
- `MYGH_DEFAULT_PER_PAGE`: Default pagination limit

## 🏗️ Development

### Project Structure

```
mygh/
├── src/mygh/               # Main package
│   ├── cli/               # CLI commands
│   │   ├── main.py        # Main CLI entry point
│   │   ├── user.py        # User-related commands
│   │   ├── repos.py       # Repository commands
│   │   ├── browse.py      # Interactive browser commands
│   │   └── search.py      # Advanced search commands
│   ├── api/               # GitHub API integration
│   │   ├── client.py      # HTTP client
│   │   └── models.py      # Pydantic models
│   ├── tui/               # Terminal User Interface
│   │   └── browser.py     # Interactive repository browser
│   ├── utils/             # Utilities
│   │   ├── config.py      # Configuration management
│   │   └── formatting.py  # Output formatting
│   └── exceptions.py      # Custom exceptions
├── tests/                 # Test suite
├── pyproject.toml        # Project configuration
├── uv.lock              # Dependency lock file
└── README.md            # This file
```

### Setting Up Development Environment

1. **Clone and setup:**
   ```bash
   git clone https://github.com/ryancheley/MyGH.git
   cd MyGH
   uv sync --dev
   ```

2. **Run tests:**
   ```bash
   uv run pytest
   ```

3. **Code formatting and linting:**
   ```bash
   uv run ruff check
   uv run ruff format
   uv run mypy src/
   ```

4. **Install in development mode:**
   ```bash
   uv sync
   ```

### Running Tests

MyGH includes a comprehensive test suite with **97% code coverage** that exceeds industry standards:

```bash
# Run all tests
uv run pytest

# Run with coverage reporting
uv run pytest --cov=src/mygh --cov-report=term-missing

# Run tests with coverage requirement (95%+)
uv run pytest --cov=src/mygh --cov-fail-under=95

# Run specific test file
uv run pytest tests/test_api_client.py

# Run tests with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov=src/mygh --cov-report=html
```

### Multi-Python Testing with Tox

MyGH supports **Python 3.10 through Python 3.14 (beta)** and uses tox for comprehensive testing across all versions:

```bash
# Install tox (if not already installed)
uv sync --dev

# Test across all Python versions (3.10-3.14)
uv run tox

# Test specific Python version
uv run tox -e py311

# Test Python 3.14 beta specifically
uv run tox -e py314-dev

# Test multiple specific versions
uv run tox -e py310,py311,py312

# Run linting across all versions
uv run tox -e lint

# Run type checking
uv run tox -e type

# Run coverage with detailed reporting
uv run tox -e coverage

# List all available test environments
uv run tox -l

# Run tests in parallel (faster)
uv run tox -p auto

# Clean and recreate all environments
uv run tox --recreate
```

#### Expected Tox Results

When running `uv run tox`, you should see results similar to:

```
py310: OK (5.80=setup[4.16]+cmd[1.64] seconds)
py311: OK (6.98=setup[5.09]+cmd[1.89] seconds)  
py312: OK (1.91=setup[0.35]+cmd[1.55] seconds)
py313: OK (5.92=setup[4.00]+cmd[1.92] seconds)
py314-dev: SKIP (0.00 seconds)  # May be skipped if Python 3.14 beta not installed
lint: FAIL/OK depending on code style
type: FAIL/OK depending on type annotations
coverage: OK (5.85=setup[3.91]+cmd[1.94] seconds)
```

- **Core Python versions (3.10-3.13)**: Should consistently pass
- **Python 3.14 beta**: May be skipped if not installed (this is expected)
- **Lint environment**: May fail with style violations that need fixing
- **Type environment**: May fail with type annotation issues
- **Coverage environment**: Should pass with 97%+ coverage

#### Tox Environments

| Environment | Description | Python Versions |
|-------------|-------------|-----------------|
| `py310` | Tests on Python 3.10 | 3.10 |
| `py311` | Tests on Python 3.11 | 3.11 |
| `py312` | Tests on Python 3.12 | 3.12 |
| `py313` | Tests on Python 3.13 | 3.13 |
| `py314-dev` | Tests on Python 3.14 (beta) | 3.14 beta* |
| `lint` | Code linting with ruff | All |
| `type` | Type checking with mypy | All |
| `coverage` | Detailed coverage report (97%+) | All |

**Note**: *Python 3.14 beta may not be available on all systems and will be skipped if not installed.

### Test Coverage Details

The test suite achieves **97% coverage** across all components:

| Component | Coverage | Focus Areas |
|-----------|----------|-------------|
| `api/models.py` | 100% | Pydantic data validation and serialization |
| `exceptions.py` | 100% | Custom exception handling |
| `cli/user.py` | 100% | User command implementations |
| `utils/formatting.py` | 98% | Output formatting (table, JSON, CSV) |
| `utils/config.py` | 97% | Configuration management |
| `cli/repos.py` | 96% | Repository command implementations |
| `cli/main.py` | 95% | Main CLI entry point and decorators |
| `api/client.py` | 92% | GitHub API client and HTTP handling |

### Test Suite Features

- **🔄 Async Testing**: Full async/await support with pytest-asyncio
- **🌐 HTTP Mocking**: Complete API mocking with respx for reliable tests
- **🎭 CLI Testing**: Comprehensive CLI command testing with Typer's test runner
- **📊 Edge Cases**: Extensive edge case coverage including error scenarios
- **⚡ Performance**: Fast test execution with parallel capabilities
- **🔧 Integration**: End-to-end testing of complete workflows

### Test Categories

```bash
# API client tests - GitHub API integration
uv run pytest tests/test_api_client.py

# CLI command tests - User interface testing
uv run pytest tests/test_cli.py

# Data model tests - Pydantic validation
uv run pytest tests/test_models.py

# Configuration tests - Settings management
uv run pytest tests/test_config.py

# Formatting tests - Output generation
uv run pytest tests/test_formatting.py

# Exception handling tests - Error scenarios
uv run pytest tests/test_exceptions.py
```

### Code Quality

The project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Pytest**: Testing framework with 97% coverage
- **pytest-cov**: Coverage reporting and enforcement
- **pytest-asyncio**: Async testing support
- **respx**: HTTP request mocking for reliable API tests

### Version Management

MyGH includes an automated version bumping script that updates both `pyproject.toml` and creates git tags to trigger releases:

```bash
# Bump patch version (0.1.1 -> 0.1.2)
uv run python bump-version.py patch

# Bump minor version (0.1.1 -> 0.2.0)
uv run python bump-version.py minor

# Bump major version (0.1.1 -> 1.0.0)
uv run python bump-version.py major
```

The script will:
1. Update the version in `pyproject.toml`
2. Create a git commit with the version change
3. Create and push a git tag (e.g., `v0.1.2`)
4. Automatically trigger the release workflow for PyPI publishing

**Requirements**: The `packaging` library is included in development dependencies.

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. **Run comprehensive tests**: `uv run pytest --cov=src/mygh --cov-fail-under=95`
5. **Test across Python versions**: `uv run tox`
6. **Run linting**: `uv run tox -e lint`
7. **Type checking**: `uv run tox -e type`
8. Commit your changes: `git commit -am 'Add some feature'`
9. Push to the branch: `git push origin feature-name`
10. Submit a pull request

#### Handling Tox Failures

If you encounter failures in specific environments:

```bash
# Fix linting issues automatically where possible
uv run ruff check --fix src tests
uv run ruff format src tests

# Check what lint issues remain
uv run tox -e lint

# Fix type checking issues
uv run mypy src/mygh

# Re-run type checking environment
uv run tox -e type

# Run only the core test environments (skip lint/type)
uv run tox -e py310,py311,py312,py313,py314-dev,coverage
```

**Note**: All contributions must maintain the 95%+ test coverage requirement and pass tests on Python 3.10-3.14 (beta). Linting and type checking issues should be resolved for production code.

## 🛠️ Built With

### Core Technologies
- **[Python 3.10+](https://python.org)** - Programming language
- **[Typer](https://typer.tiangolo.com/)** - CLI framework
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting
- **[httpx](https://www.python-httpx.org/)** - Async HTTP client
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation
- **[uv](https://github.com/astral-sh/uv)** - Modern package manager

### Testing & Quality
- **[pytest](https://pytest.org/)** - Testing framework
- **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)** - Async testing support
- **[pytest-cov](https://pytest-cov.readthedocs.io/)** - Coverage reporting
- **[respx](https://lundberg.github.io/respx/)** - HTTP request mocking
- **[tox](https://tox.wiki/)** - Multi-Python version testing (3.10-3.14 beta)
- **[ruff](https://github.com/astral-sh/ruff)** - Fast linting and formatting
- **[mypy](https://mypy.readthedocs.io/)** - Static type checking

## 📋 API Reference

### GitHub API Integration

MyGH integrates with the GitHub REST API v3 and handles:

- **Authentication**: Personal access tokens and GitHub CLI integration
- **Rate Limiting**: Automatic handling of API rate limits
- **Error Handling**: Comprehensive error messages and retry logic
- **Pagination**: Efficient handling of paginated responses

### Supported Endpoints

- `/user` - Authenticated user information
- `/users/{username}` - User information
- `/user/starred` - Starred repositories
- `/users/{username}/starred` - User's starred repositories
- `/user/repos` - User repositories
- `/users/{username}/repos` - User's repositories
- `/user/gists` - User gists
- `/users/{username}/gists` - User's gists
- `/repos/{owner}/{repo}/issues` - Repository issues

## 🚨 Error Handling

MyGH provides clear error messages for common scenarios:

- **Authentication Errors**: Clear instructions for setting up tokens
- **API Rate Limits**: Informative messages about rate limit status
- **Network Issues**: Retry logic for transient failures
- **Invalid Parameters**: Helpful parameter validation messages

## 🔒 Security

- **Token Security**: GitHub tokens are never logged or displayed
- **Configuration**: Tokens are not saved to configuration files
- **Environment**: Secure handling of environment variables
- **HTTPS**: All API communications use HTTPS

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: Check this README and built-in help (`mygh --help`)
- **Issues**: Report bugs and request features via GitHub Issues
- **GitHub API**: Refer to [GitHub REST API documentation](https://docs.github.com/en/rest)

## 🎯 Roadmap

- [ ] [Interactive repository browser](https://github.com/ryancheley/MyGH/issues/1)
- [ ] [Repository creation and management](https://github.com/ryancheley/MyGH/issues/2)
- [ ] [Pull request management](https://github.com/ryancheley/MyGH/issues/3)
- [ ] [GitHub Actions integration](https://github.com/ryancheley/MyGH/issues/4)
- [ ] [Organization management](https://github.com/ryancheley/MyGH/issues/5)
- [ ] [Advanced search capabilities](https://github.com/ryancheley/MyGH/issues/6)
- [ ] [Notification management](https://github.com/ryancheley/MyGH/issues/7)
- [ ] [Team management features](https://github.com/ryancheley/MyGH/issues/8)

---

**Made with ❤️ using modern Python tooling**