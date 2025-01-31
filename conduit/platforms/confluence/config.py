from dataclasses import dataclass


@dataclass
class ConfluenceConfig:
    """Configuration for Confluence."""

    url: str
    email: str
    api_token: str
