# MyGH Development and Deployment Automation
# Requires: just, uv, git

# Default recipe shows available commands
default:
    @just --list

# Install dependencies and setup development environment
setup:
    @echo "🔧 Setting up development environment..."
    uv sync --dev
    @echo "✅ Development environment ready!"

# Run all tests with coverage
test:
    @echo "🧪 Running test suite..."
    uv run pytest --cov=src/mygh --cov-fail-under=95
    @echo "✅ All tests passed!"

# Run tests across all Python versions
test-all:
    @echo "🐍 Running tests across all Python versions..."
    uv run tox
    @echo "✅ Multi-Python testing complete!"

# Run code quality checks
lint:
    @echo "🔍 Running code quality checks..."
    uv run ruff check src tests
    uv run ruff format --check src tests
    uv run mypy src/mygh
    @echo "✅ Code quality checks passed!"

# Fix code formatting and linting issues
fix:
    @echo "🛠️ Fixing code formatting and linting issues..."
    uv run ruff format src tests
    uv run ruff check --fix src tests
    @echo "✅ Code formatting fixed!"

# Build the package
build:
    @echo "📦 Building package..."
    uv build
    @echo "✅ Package built successfully!"

# Clean build artifacts
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf dist/
    rm -rf build/
    rm -rf *.egg-info/
    rm -rf .coverage
    rm -rf htmlcov/
    rm -rf .pytest_cache/
    rm -rf .tox/
    @echo "✅ Build artifacts cleaned!"

# Get current version from pyproject.toml
current-version:
    @uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# Bump version (patch, minor, or major)
bump-version type:
    #!/usr/bin/env bash
    set -euo pipefail
    
    echo "📈 Bumping {{type}} version..."
    
    # Get current version
    current=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    echo "Current version: $current"
    
    # Parse version components
    IFS='.' read -ra VERSION <<< "$current"
    major=${VERSION[0]}
    minor=${VERSION[1]}
    patch=${VERSION[2]}
    
    # Bump version based on type
    case "{{type}}" in
        "patch")
            patch=$((patch + 1))
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        *)
            echo "❌ Invalid version type. Use: patch, minor, or major"
            exit 1
            ;;
    esac
    
    new_version="$major.$minor.$patch"
    echo "New version: $new_version"
    
    # Update pyproject.toml
    sed -i.bak "s/version = \"$current\"/version = \"$new_version\"/" pyproject.toml && rm pyproject.toml.bak
    
    # Update __init__.py
    sed -i.bak "s/__version__ = \"$current\"/__version__ = \"$new_version\"/" src/mygh/__init__.py && rm src/mygh/__init__.py.bak
    
    # Update test file
    sed -i.bak "s/assert __version__ == \"$current\"/assert __version__ == \"$new_version\"/" tests/test_cli.py && rm tests/test_cli.py.bak
    
    echo "✅ Version bumped to $new_version in all files!"

# Validate that all version references are consistent
validate-version:
    #!/usr/bin/env bash
    set -euo pipefail
    
    echo "🔍 Validating version consistency..."
    
    # Get versions from all files
    pyproject_version=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
    init_version=$(uv run python -c "import sys; sys.path.insert(0, 'src'); from mygh import __version__; print(__version__)")
    test_version=$(grep "assert __version__ ==" tests/test_cli.py | sed 's/.*== "\(.*\)".*/\1/')
    
    echo "pyproject.toml: $pyproject_version"
    echo "__init__.py: $init_version"
    echo "test_cli.py: $test_version"
    
    if [[ "$pyproject_version" == "$init_version" && "$init_version" == "$test_version" ]]; then
        echo "✅ All versions are consistent!"
        echo "Current version: $pyproject_version"
    else
        echo "❌ Version mismatch detected!"
        exit 1
    fi

# Pre-release checks - run all quality checks before release
pre-release:
    @echo "🚀 Running pre-release checks..."
    @just validate-version
    @just lint
    @just test
    @just build
    @echo "✅ All pre-release checks passed! Ready for release."

# Release with automatic version bumping
release type="patch":
    #!/usr/bin/env bash
    set -euo pipefail
    
    echo "🚀 Starting release process..."
    
    # Check if working directory is clean
    if [[ -n $(git status --porcelain) ]]; then
        echo "❌ Working directory is not clean. Commit or stash changes first."
        exit 1
    fi
    
    # Check if on main branch
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "main" ]]; then
        echo "❌ Must be on main branch for release. Current branch: $current_branch"
        exit 1
    fi
    
    # Pull latest changes
    echo "📥 Pulling latest changes..."
    git pull origin main
    
    # Bump version
    just bump-version {{type}}
    
    # Get new version
    new_version=$(just current-version)
    echo "🔖 Releasing version $new_version"
    
    # Run pre-release checks
    just pre-release
    
    # Commit version changes
    echo "💾 Committing version changes..."
    git add pyproject.toml src/mygh/__init__.py tests/test_cli.py
    git commit -m "🔖 Bump version to $new_version for release

    - Update version across all files for consistency
    - Ready for PyPI deployment
    
    🤖 Generated with [Claude Code](https://claude.ai/code)
    
    Co-Authored-By: Claude <noreply@anthropic.com>"
    
    # Create and push tag
    echo "🏷️ Creating and pushing tag v$new_version..."
    git tag "v$new_version"
    git push origin main
    git push origin "v$new_version"
    
    echo "🎉 Release v$new_version initiated!"
    echo "📦 Check GitHub Actions for deployment progress:"
    echo "   https://github.com/ryancheley/MyGH/actions"
    echo "📋 Package will be available at:"
    echo "   https://pypi.org/project/mygh/"

# Quick development workflow
dev:
    @echo "⚡ Quick development setup..."
    @just setup
    @just test
    @echo "✅ Ready for development!"

# Emergency manual deployment (use only if automated deployment fails)
deploy-manual:
    #!/usr/bin/env bash
    set -euo pipefail
    
    echo "⚠️ Manual deployment - use only in emergencies!"
    echo "This requires PyPI credentials to be configured."
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    just build
    
    echo "📤 Uploading to TestPyPI..."
    uv run twine upload --repository testpypi dist/*
    
    read -p "TestPyPI upload successful. Upload to PyPI? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Uploading to PyPI..."
        uv run twine upload dist/*
        echo "✅ Manual deployment complete!"
    fi

# Show release workflow help
release-help:
    @echo "🚀 MyGH Release Workflow"
    @echo ""
    @echo "For automated releases (recommended):"
    @echo "  just release patch    # Bump patch version (0.1.4 → 0.1.5)"
    @echo "  just release minor    # Bump minor version (0.1.4 → 0.2.0)"
    @echo "  just release major    # Bump major version (0.1.4 → 1.0.0)"
    @echo ""
    @echo "For manual version control:"
    @echo "  just bump-version patch    # Just bump version, no release"
    @echo "  just validate-version      # Check version consistency"
    @echo "  just pre-release          # Run all checks before release"
    @echo ""
    @echo "The release process will:"
    @echo "  1. Validate working directory is clean"
    @echo "  2. Ensure you're on main branch"
    @echo "  3. Pull latest changes"
    @echo "  4. Bump version in all files"
    @echo "  5. Run tests and quality checks"
    @echo "  6. Commit and tag the release"
    @echo "  7. Push to GitHub (triggers automated deployment)"