# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MyGH is a comprehensive GitHub CLI tool built with Python, Typer, and Rich. It provides GitHub user insights and repository management through a modern command-line interface with beautiful output formatting.

**Key Technologies:**
- Python 3.10+ (supports up to 3.14 beta)
- Typer framework for CLI commands
- Rich for terminal output formatting
- httpx for async HTTP client
- Pydantic for data validation
- uv for package management

## Development Commands

### Package Management
```bash
# Install dependencies and development tools
uv sync --dev

# Install without dev dependencies
uv sync

# Run the CLI tool
uv run mygh --help
```

### Testing
```bash
# Run all tests with coverage (requires 95%+ coverage)
uv run pytest --cov=src/mygh --cov-fail-under=95

# Run specific test file
uv run pytest tests/test_api_client.py

# Run tests with verbose output
uv run pytest -v

# Generate HTML coverage report
uv run pytest --cov=src/mygh --cov-report=html
```

### Multi-Python Testing with Tox
```bash
# Test across all Python versions (3.10-3.14)
uv run tox

# Test specific Python version
uv run tox -e py311

# Run linting and formatting checks
uv run tox -e lint

# Run type checking
uv run tox -e type

# Run tests with detailed coverage reporting
uv run tox -e coverage

# Run tests in parallel (faster)
uv run tox -p auto
```

### Code Quality
```bash
# Run linting checks
uv run ruff check src tests

# Format code automatically
uv run ruff format src tests

# Run type checking
uv run mypy src/mygh

# Fix linting issues automatically
uv run ruff check --fix src tests
```

### Git Branching

All new features must be done on their own branch. The name of the branch should be feature/issue-title-issue-number. For example, if the issue title was `Feature: Advanced search capabilities #6` the branch created would be `feature/feature-advanced-search-capabilities-6`

### Building and Publishing
```bash
# Build the package
uv run tox -e build

# Clean build artifacts
uv run tox -e clean
```

## Architecture Overview

### CLI Layer (`src/mygh/cli/`)
- **`main.py`**: Main CLI entry point, global exception handling, configuration commands
- **`user.py`**: User-related commands (info, starred repos, gists)
- **`repos.py`**: Repository management commands (list, info, issues)

### API Layer (`src/mygh/api/`)
- **`client.py`**: GitHub REST API client with async support, authentication, and rate limiting
- **`models.py`**: Pydantic data models for GitHub API responses

### Utils Layer (`src/mygh/utils/`)
- **`config.py`**: TOML-based configuration management with environment variable support
- **`formatting.py`**: Multi-format output (Rich tables, JSON, CSV) with commit age indicators

### Exception Handling (`src/mygh/exceptions.py`)
Custom exception classes for different error scenarios

## Authentication Architecture

The tool supports multiple authentication methods in order of precedence:
1. `GITHUB_TOKEN` environment variable
2. `GH_TOKEN` environment variable (GitHub CLI compatibility)
3. GitHub CLI authentication (`gh auth status`)

Authentication is handled by the `GitHubClient` class in `api/client.py` with automatic token validation and rate limit management.

## Configuration System

Configuration is managed through:
- **File**: `~/.config/mygh/config.toml` (TOML format)
- **Environment Variables**: `MYGH_*` prefix for settings
- **Defaults**: Sensible defaults for all options

Key configuration options:
- `output-format`: Default output format (table, json, csv)
- `default-per-page`: Default pagination limit
- Authentication tokens (never saved to config files)

## Output Formatting

The formatting system (`utils/formatting.py`) provides:
- **Rich Tables**: Colorized terminal output with commit age indicators
- **JSON Export**: Machine-readable format for automation
- **CSV Export**: Data analysis format for repositories
- **Consistent Styling**: Unified color scheme and formatting across all commands

## Error Handling Strategy

Global error handling is implemented through:
- **Decorator Pattern**: `@handle_errors` decorator in `main.py`
- **Custom Exceptions**: Specific exception types for different error scenarios
- **User-Friendly Messages**: Clear, actionable error messages
- **API Rate Limiting**: Automatic handling of GitHub API rate limits

## Testing Architecture

The test suite achieves 97% coverage with:
- **Async Testing**: Full async/await support with pytest-asyncio
- **HTTP Mocking**: Complete API mocking with respx
- **CLI Testing**: Command testing with Typer's test utilities
- **Multi-Python**: Tox testing across Python 3.10-3.14 (beta)

Test organization:
- `tests/test_api_client.py`: GitHub API client tests
- `tests/test_*_coverage.py`: Comprehensive coverage tests
- `tests/test_*_extended.py`: Extended functionality tests

## Development Workflow

1. **Setup**: `uv sync --dev`
2. **Development**: Make changes to `src/mygh/`
3. **Testing**: `uv run pytest --cov=src/mygh --cov-fail-under=95`
4. **Multi-Python**: `uv run tox` (tests across Python versions)
5. **Code Quality**: `uv run tox -e lint,type`
6. **Build**: `uv run tox -e build`

## Key Design Patterns

- **Dependency Injection**: GitHub client is injected into CLI commands
- **Async/Await**: All API calls use async patterns for performance
- **Type Safety**: Comprehensive type hints with strict MyPy configuration
- **Configuration Layering**: Environment variables override config file settings
- **Error Propagation**: Errors bubble up through layers with appropriate handling

## Common Development Tasks

### Adding a New CLI Command
1. Add command function to appropriate module in `src/mygh/cli/`
2. Use type hints and proper error handling
3. Add tests in corresponding test file
4. Update documentation if needed

### Adding API Integration
1. Add new methods to `GitHubClient` in `src/mygh/api/client.py`
2. Create Pydantic models in `src/mygh/api/models.py`
3. Add comprehensive tests with HTTP mocking
4. Handle rate limiting and error scenarios

### Testing a Single Command
```bash
# Test specific CLI command
uv run pytest tests/test_user.py::test_user_info_command -v

# Test with coverage for specific module
uv run pytest tests/test_repos.py --cov=src/mygh/cli/repos --cov-report=term-missing
```