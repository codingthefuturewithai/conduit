from pathlib import Path
import yaml
from pydantic import BaseModel

from conduit.core.exceptions import ConfigurationError
from conduit.platforms.jira.config import JiraConfig

class Config(BaseModel):
    """Base configuration class."""
    jira: JiraConfig

def load_config() -> Config:
    """Load configuration from YAML file."""
    config_path = Path.home() / ".config" / "conduit" / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}. "
            "Please create this file with your Jira credentials:\n"
            "jira:\n"
            "  url: 'https://your-domain.atlassian.net'\n"
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
