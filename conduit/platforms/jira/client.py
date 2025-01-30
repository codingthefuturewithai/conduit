from atlassian import Jira
from conduit.platforms.base import Platform, IssueManager
from conduit.core.config import load_config
from conduit.core.exceptions import ConfigurationError, PlatformError
import logging
from typing import Any, Dict

from conduit.core.logger import logger

class JiraClient(Platform, IssueManager):
    def __init__(self):
        try:
            self.config = load_config().jira
            self.jira = None
            logger.info("Initialized Jira client")
        except (FileNotFoundError, ConfigurationError) as e:
            logger.error(f"Failed to initialize Jira client: {e}")
            raise

    def connect(self) -> None:
        logger.info("Connecting to Jira...")
        try:
            if not self.jira:
                self.jira = Jira(
                    url=self.config.url,
                    token=self.config.api_token
                )
                logger.info("Connected to Jira successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            raise PlatformError(f"Failed to connect to Jira: {e}")

    def disconnect(self) -> None:
        self.jira = None

    def get(self, key: str) -> Dict[str, Any]:
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            issue = self.jira.issue(key)
            return issue.raw if hasattr(issue, 'raw') else issue
        except Exception as e:
            raise PlatformError(f"Failed to get issue {key}: {e}")

    def search(self, query: str) -> list[Dict[str, Any]]:
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            result = self.jira.jql(query)
            return result['issues']
        except Exception as e:
            raise PlatformError(f"Failed to search issues with query '{query}': {e}")

    def create(self, **kwargs) -> Dict[str, Any]:
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            return self.jira.create_issue(**kwargs)
        except Exception as e:
            raise PlatformError(f"Failed to create issue: {e}")

    def update(self, key: str, **kwargs) -> None:
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            self.jira.issue_update(key, kwargs)
        except Exception as e:
            raise PlatformError(f"Failed to update issue {key}: {e}")
