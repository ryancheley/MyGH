"""Tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from mygh.utils.config import Config, ConfigManager


class TestConfig:
    """Test Config model."""

    def test_config_defaults(self):
        """Test config with default values."""
        config = Config()

        assert config.github_token is None
        assert config.output_format == "table"
        assert config.default_per_page == 30

    def test_config_with_values(self):
        """Test config with provided values."""
        config = Config(
            github_token="test_token",
            output_format="json",
            default_per_page=50,
        )

        assert config.github_token == "test_token"
        assert config.output_format == "json"
        assert config.default_per_page == 50

    def test_config_with_aliases(self):
        """Test config with field aliases."""
        config = Config(
            **{
                "github-token": "test_token",
                "output-format": "csv",
                "default-per-page": 100,
            }
        )

        assert config.github_token == "test_token"
        assert config.output_format == "csv"
        assert config.default_per_page == 100

    def test_config_field_validation(self):
        """Test config field validation."""
        # Valid values should work
        config = Config(output_format="table")
        assert config.output_format == "table"

        # Invalid types should be caught by pydantic
        with pytest.raises(ValueError):
            Config(default_per_page="not_a_number")


class TestConfigManager:
    """Test ConfigManager."""

    def test_config_manager_init(self):
        """Test ConfigManager initialization."""
        manager = ConfigManager()

        assert manager.config_dir == Path.home() / ".config" / "mygh"
        assert manager.config_file == manager.config_dir / "config.toml"
        assert manager._config is None

    def test_ensure_config_dir(self, temp_config_dir):
        """Test ensuring config directory exists."""
        manager = ConfigManager()
        manager._ensure_config_dir()

        assert manager.config_dir.exists()
        assert manager.config_dir.is_dir()

    def test_load_config_no_file(self, temp_config_dir):
        """Test loading config when no file exists."""
        # Clear environment variables that could affect the test
        with patch.dict(os.environ, {}, clear=True):
            manager = ConfigManager()
            config = manager.load_config()

            # Should return default config
            assert isinstance(config, Config)
            assert config.output_format == "table"
            assert config.default_per_page == 30
            assert config.github_token is None

    def test_load_config_with_file(self, temp_config_dir):
        """Test loading config from file."""
        manager = ConfigManager()

        # Create a config file
        config_content = """
output-format = "json"
default-per-page = 50
"""
        manager.config_file.write_text(config_content)

        config = manager.load_config()
        assert config.output_format == "json"
        assert config.default_per_page == 50

    def test_load_config_with_invalid_file(self, temp_config_dir):
        """Test loading config with invalid TOML file."""
        manager = ConfigManager()

        # Create an invalid config file
        manager.config_file.write_text("invalid toml content [")

        # Should fall back to defaults
        config = manager.load_config()
        assert config.output_format == "table"
        assert config.default_per_page == 30

    def test_load_config_with_env_vars(self, temp_config_dir):
        """Test loading config with environment variable overrides."""
        with patch.dict(
            os.environ,
            {
                "GITHUB_TOKEN": "env_token",
                "MYGH_OUTPUT_FORMAT": "csv",
                "MYGH_DEFAULT_PER_PAGE": "75",
            },
        ):
            manager = ConfigManager()
            config = manager.load_config()

            assert config.github_token == "env_token"
            assert config.output_format == "csv"
            assert config.default_per_page == 75

    def test_load_config_env_vars_override_file(self, temp_config_dir):
        """Test that environment variables override file values."""
        manager = ConfigManager()

        # Create a config file using snake_case to match the internal format
        config_content = """
output_format = "json"
default_per_page = 50
"""
        manager.config_file.write_text(config_content)

        with patch.dict(
            os.environ,
            {
                "MYGH_OUTPUT_FORMAT": "csv",
            },
        ):
            # Clear any cached config to ensure fresh load
            manager._config = None
            config = manager.load_config()

            # Env var should override file
            assert config.output_format == "csv"
            # File value should still be used for non-overridden fields
            assert config.default_per_page == 50

    def test_load_config_invalid_env_var(self, temp_config_dir):
        """Test loading config with invalid environment variable."""
        with patch.dict(
            os.environ,
            {
                "MYGH_DEFAULT_PER_PAGE": "not_a_number",
            },
        ):
            manager = ConfigManager()
            config = manager.load_config()

            # Should ignore invalid env var and use default
            assert config.default_per_page == 30

    def test_load_config_caching(self, temp_config_dir):
        """Test that config is cached after first load."""
        manager = ConfigManager()

        config1 = manager.load_config()
        config2 = manager.load_config()

        # Should return the same instance
        assert config1 is config2

    def test_save_config(self, temp_config_dir):
        """Test saving config to file."""
        manager = ConfigManager()

        config = Config(
            output_format="json",
            default_per_page=75,
        )

        manager.save_config(config)

        # Config file should exist and contain the values
        assert manager.config_file.exists()
        content = manager.config_file.read_text()
        assert 'output-format = "json"' in content
        assert "default-per-page = 75" in content

    def test_save_config_excludes_github_token(self, temp_config_dir):
        """Test that github token is not saved to file."""
        manager = ConfigManager()

        config = Config(
            github_token="secret_token",
            output_format="json",
        )

        manager.save_config(config)

        content = manager.config_file.read_text()
        assert "secret_token" not in content
        assert "github-token" not in content

    def test_dict_to_toml(self, temp_config_dir):
        """Test converting dictionary to TOML format."""
        manager = ConfigManager()

        data = {
            "output-format": "json",
            "default-per-page": 50,
            "bool-value": True,
        }

        result = manager._dict_to_toml(data)

        assert 'output-format = "json"' in result
        assert "default-per-page = 50" in result
        assert "bool-value = True" in result

    def test_get_config(self, temp_config_dir):
        """Test get_config method."""
        manager = ConfigManager()

        config = manager.get_config()

        assert isinstance(config, Config)
        # Should be the same as load_config
        assert config is manager.load_config()

    def test_set_config_value(self, temp_config_dir):
        """Test setting a config value."""
        manager = ConfigManager()

        manager.set_config_value("output-format", "csv")

        # Should update the cached config
        config = manager.get_config()
        assert config.output_format == "csv"

        # Should save to file
        assert manager.config_file.exists()
        content = manager.config_file.read_text()
        assert 'output-format = "csv"' in content

    def test_set_config_value_with_underscore_key(self, temp_config_dir):
        """Test setting config value with underscore key."""
        manager = ConfigManager()

        manager.set_config_value("output_format", "json")

        config = manager.get_config()
        assert config.output_format == "json"

    def test_set_config_value_invalid_key(self, temp_config_dir):
        """Test setting config value with invalid key."""
        manager = ConfigManager()

        with pytest.raises(ValueError, match="Unknown configuration key"):
            manager.set_config_value("invalid-key", "value")

    def test_list_config(self, temp_config_dir):
        """Test listing config values."""
        manager = ConfigManager()

        # Set some config values
        manager.set_config_value("output-format", "json")
        manager.set_config_value("default-per-page", 75)

        config_dict = manager.list_config()

        assert config_dict["output-format"] == "json"
        assert config_dict["default-per-page"] == 75
        # Should not include github-token even if it was set
        assert "github-token" not in config_dict

    def test_list_config_excludes_none_values(self, temp_config_dir):
        """Test that list_config excludes None values."""
        manager = ConfigManager()

        config_dict = manager.list_config()

        # Should only include non-None values
        assert "output-format" in config_dict
        assert "default-per-page" in config_dict
        # github_token is None by default, so shouldn't be included
        assert "github-token" not in config_dict

    def test_config_file_permissions(self, temp_config_dir):
        """Test that config file is created with appropriate permissions."""
        manager = ConfigManager()

        config = Config(output_format="json")
        manager.save_config(config)

        # File should exist and be readable
        assert manager.config_file.exists()
        assert manager.config_file.is_file()

        # Should be able to read it back
        content = manager.config_file.read_text()
        assert 'output-format = "json"' in content

    def test_concurrent_config_access(self, temp_config_dir):
        """Test concurrent access to config doesn't cause issues."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()

        # Both managers should work independently
        config1 = manager1.get_config()
        config2 = manager2.get_config()

        assert isinstance(config1, Config)
        assert isinstance(config2, Config)

        # Changes through one manager should not affect the other's cache
        manager1.set_config_value("output-format", "json")

        # manager2's cache should still be unchanged
        assert manager2._config.output_format == "table"

        # But reloading should pick up the changes
        manager2._config = None  # Clear cache
        new_config2 = manager2.get_config()
        assert new_config2.output_format == "json"

    @patch.dict(os.environ, {}, clear=True)
    def test_all_env_vars_cleared(self, temp_config_dir):
        """Test config loading with all environment variables cleared."""
        manager = ConfigManager()
        config = manager.load_config()

        # Should use all defaults
        assert config.github_token is None
        assert config.output_format == "table"
        assert config.default_per_page == 30

    def test_config_manager_state_isolation(self, temp_config_dir):
        """Test that ConfigManager instances don't share state."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()

        # Load config in first manager
        config1 = manager1.load_config()

        # Second manager should have its own state
        assert manager2._config is None

        # Loading config in second manager shouldn't affect first
        config2 = manager2.load_config()

        assert config1 is not config2
        assert manager1._config is not manager2._config
