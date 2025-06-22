"""Configuration management for MyGH."""

import os
from pathlib import Path
from typing import Any

try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found]
from pydantic import BaseModel, ConfigDict, Field


class Config(BaseModel):
    """MyGH configuration model."""

    github_token: str | None = Field(default=None, alias="github-token")
    output_format: str = Field(default="table", alias="output-format")
    default_per_page: int = Field(default=30, alias="default-per-page")

    model_config = ConfigDict(populate_by_name=True)


class ConfigManager:
    """Configuration manager for MyGH."""

    def __init__(self) -> None:
        self.config_dir = Path.home() / ".config" / "mygh"
        self.config_file = self.config_dir / "config.toml"
        self._config: Config | None = None

    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Config:
        """Load configuration from file and environment variables."""
        if self._config is not None:
            return self._config

        config_data: dict[str, Any] = {}

        # Load from config file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, "rb") as f:
                    config_data = tomllib.load(f)
            except Exception:
                pass  # Ignore config file errors, use defaults

        # Override with environment variables
        env_mapping = {
            "GITHUB_TOKEN": "github_token",
            "MYGH_OUTPUT_FORMAT": "output_format",
            "MYGH_DEFAULT_PER_PAGE": "default_per_page",
        }

        for env_var, config_key in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if config_key == "default_per_page":
                    try:
                        config_data[config_key] = int(value)
                    except ValueError:
                        pass
                else:
                    config_data[config_key] = value

        self._config = Config(**config_data)
        return self._config

    def save_config(self, config: Config) -> None:
        """Save configuration to file."""
        self._ensure_config_dir()

        config_dict = config.model_dump(by_alias=True, exclude_none=True)

        # Don't save github_token to file for security
        config_dict.pop("github-token", None)

        toml_content = self._dict_to_toml(config_dict)

        with open(self.config_file, "w") as f:
            f.write(toml_content)

    def _dict_to_toml(self, data: dict[str, Any]) -> str:
        """Convert dictionary to TOML format."""
        lines = []
        for key, value in data.items():
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            else:
                lines.append(f"{key} = {value}")
        return "\n".join(lines) + "\n"

    def get_config(self) -> Config:
        """Get current configuration."""
        return self.load_config()

    def set_config_value(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        config = self.load_config()

        # Map CLI keys to model fields
        key_mapping = {
            "output-format": "output_format",
            "default-per-page": "default_per_page",
            "github-token": "github_token",
        }

        field_name = key_mapping.get(key, key.replace("-", "_"))

        if hasattr(config, field_name):
            setattr(config, field_name, value)
            self.save_config(config)
            self._config = config
        else:
            raise ValueError(f"Unknown configuration key: {key}")

    def list_config(self) -> dict[str, Any]:
        """List all configuration values."""
        config = self.load_config()
        config_dict = config.model_dump(by_alias=True, exclude_none=True)

        # Don't show github_token for security
        config_dict.pop("github-token", None)

        return config_dict
