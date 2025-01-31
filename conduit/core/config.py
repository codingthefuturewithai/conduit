from pathlib import Path
import yaml
from pydantic import BaseModel

from conduit.core.exceptions import ConfigurationError


class JiraConfig(BaseModel):
    """Jira configuration."""

    url: str
    email: str
    api_token: str


class ConfluenceConfig(BaseModel):
    """Confluence configuration."""

    url: str
    email: str
    api_token: str


class Config(BaseModel):
    """Base configuration class."""

    jira: JiraConfig
    confluence: ConfluenceConfig


def load_config() -> Config:
    """Load configuration from YAML file."""
    config_path = Path.home() / ".config" / "conduit" / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}. "
            "Please create this file with your credentials:\n"
            "jira:\n"
            "  url: 'https://your-domain.atlassian.net'\n"
            "  email: 'your-email@example.com'\n"
            "  api_token: 'your-api-token'\n\n"
            "confluence:\n"
            "  url: 'https://your-domain.atlassian.net'\n"
            "  email: 'your-email@example.com'\n"
            "  api_token: 'your-api-token'"
        )

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return Config(**data)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading config: {e}")
