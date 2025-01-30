from atlassian import Jira
from conduit.platforms.base import Platform, IssueManager
from conduit.core.config import load_config
from conduit.core.exceptions import PlatformError
from typing import Any, Dict

class JiraClient(Platform, IssueManager):
    def __init__(self):
        self.config = load_config().jira
        self.jira = None

    def connect(self) -> None:
        try:
            self.jira = Jira(
                url=self.config.url,
                token=self.config.api_token
            )
        except Exception as e:
            raise PlatformError(f"Failed to connect to Jira: {e}")

    def disconnect(self) -> None:
        self.jira = None

    def get(self, key: str) -> Dict[str, Any]:
        try:
            return self.jira.issue(key)
        except Exception as e:
            raise PlatformError(f"Failed to get issue {key}: {e}")

    def search(self, query: str) -> list[Dict[str, Any]]:
        try:
            return self.jira.jql(query)
        except Exception as e:
            raise PlatformError(f"Failed to search issues with query '{query}': {e}")

    def create(self, **kwargs) -> Dict[str, Any]:
        try:
            return self.jira.create_issue(fields=kwargs)
        except Exception as e:
            raise PlatformError(f"Failed to create issue: {e}")

    def update(self, key: str, **kwargs) -> None:
        try:
            self.jira.update_issue(key, fields=kwargs)
        except Exception as e:
            raise PlatformError(f"Failed to update issue {key}: {e}")
