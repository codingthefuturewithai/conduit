from pathlib import Path
import yaml
import shutil
import os
import importlib.resources as pkg_resources
from pydantic import BaseModel
from typing import Dict, Optional

from conduit.core.exceptions import ConfigurationError
from conduit.core.logger import logger


class SiteConfig(BaseModel):
    """Configuration for a single Atlassian site."""

    url: str
    email: str
    api_token: str


class JiraConfig(BaseModel):
    """Jira configuration."""

    default_site_alias: str = "default"  # Field alias for YAML compatibility
    sites: Dict[str, SiteConfig]

    class Config:
        alias_generator = lambda string: string.replace("_", "-")
        populate_by_alias = True

    def get_site_config(self, site_alias: Optional[str] = None) -> SiteConfig:
        """Get the configuration for a specific site or the default site."""
        alias = site_alias or self.default_site_alias
        if alias not in self.sites:
            raise ConfigurationError(f"Site configuration not found for alias: {alias}")
        return self.sites[alias]


class ConfluenceConfig(BaseModel):
    """Confluence configuration."""

    url: str  # Default URL
    email: str  # Default email
    api_token: str  # Default API token
    sites: Dict[str, SiteConfig]

    def get_site_config(self, site_alias: Optional[str] = None) -> SiteConfig:
        """Get the configuration for a specific site or the default site."""
        if not site_alias:
            return SiteConfig(url=self.url, email=self.email, api_token=self.api_token)
        if site_alias not in self.sites:
            raise ConfigurationError(
                f"Site configuration not found for alias: {site_alias}"
            )
        return self.sites[site_alias]


class Config(BaseModel):
    """Base configuration class."""

    jira: JiraConfig
    confluence: ConfluenceConfig


def get_config_dir() -> Path:
    """Get the configuration directory path based on the OS."""
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA")) / "conduit"
    else:  # Unix-like systems
        config_dir = Path.home() / ".config" / "conduit"
    return config_dir


def create_default_config(config_path: Path) -> None:
    """Create the default configuration file."""
    config_dir = config_path.parent

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Copy default config from package
    try:
        with pkg_resources.path("conduit.config", "config.yaml") as default_config:
            shutil.copy(default_config, config_path)
        logger.info(f"Created default configuration file at {config_path}")
    except Exception as e:
        raise ConfigurationError(f"Failed to create default config: {e}")


def load_config() -> Config:
    """Load configuration from YAML file."""
    config_path = get_config_dir() / "config.yaml"

    if not config_path.exists():
        raise ConfigurationError(
            f"Configuration file not found at {config_path}. "
            "Run 'conduit --init' to create a default configuration file."
        )

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return Config(**data)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading config: {e}")
