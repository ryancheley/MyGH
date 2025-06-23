#!/usr/bin/env python3
"""
Simple script to bump version using git tags and update pyproject.toml.
Usage:
  python bump-version.py patch   # 0.1.1 -> 0.1.2
  python bump-version.py minor   # 0.1.1 -> 0.2.0
  python bump-version.py major   # 0.1.1 -> 1.0.0
"""

import re
import subprocess
import sys
from pathlib import Path

from packaging import version


def get_latest_tag():
    """Get the latest git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "v0.0.0"


def bump_version(current_version, bump_type):
    """Bump version based on type."""
    v = version.Version(current_version)

    if bump_type == "patch":
        new_version = f"{v.major}.{v.minor}.{v.micro + 1}"
    elif bump_type == "minor":
        new_version = f"{v.major}.{v.minor + 1}.0"
    elif bump_type == "major":
        new_version = f"{v.major + 1}.0.0"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

    return new_version


def update_pyproject_version(new_version):
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found in current directory")
    
    content = pyproject_path.read_text()
    
    # Update version line
    pattern = r'^version = "[^"]*"'
    replacement = f'version = "{new_version}"'
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content == new_content:
        raise ValueError("Could not find version line in pyproject.toml")
    
    pyproject_path.write_text(new_content)
    print(f"Updated pyproject.toml version to {new_version}")


def create_tag_and_commit(new_version):
    """Update pyproject.toml, commit changes, and create/push git tag."""
    tag_name = f"v{new_version}"
    
    # Update pyproject.toml
    update_pyproject_version(new_version)
    
    # Stage and commit the version change
    subprocess.run(["git", "add", "pyproject.toml"], check=True)
    commit_msg = f"🔖 Bump version to {new_version} for release"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
    
    # Create annotated tag
    tag_msg = f"Release {new_version}"
    subprocess.run(["git", "tag", "-a", tag_name, "-m", tag_msg], check=True)
    
    # Push commit and tag
    subprocess.run(["git", "push", "origin", "main"], check=True)
    subprocess.run(["git", "push", "origin", tag_name], check=True)
    
    print(f"Created and pushed commit and tag: {tag_name}")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["patch", "minor", "major"]:
        print(__doc__)
        sys.exit(1)

    bump_type = sys.argv[1]

    # Get current version from latest tag
    current_tag = get_latest_tag()
    current_version = current_tag.lstrip("v") if current_tag.startswith("v") else current_tag

    print(f"Current version: {current_version}")

    # Bump version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version}")

    # Confirm
    response = input(f"Update pyproject.toml and create tag v{new_version}? (y/N): ")
    if response.lower() != "y":
        print("Cancelled")
        sys.exit(0)

    try:
        # Update files and create tag
        create_tag_and_commit(new_version)
        print(f"✅ Version bumped to {new_version}")
        print(f"🚀 Release workflow should start automatically for v{new_version}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()