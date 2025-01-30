from pathlib import Path
import yaml
from pydantic import BaseModel

class JiraConfig(BaseModel):
    url: str
    api_token: str

class Config(BaseModel):
    jira: JiraConfig

def load_config() -> Config:
    """Load configuration from YAML file."""
    config_path = Path.home() / ".config" / "conduit" / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path) as f:
        data = yaml.safe_load(f)
    
    return Config(**data)
