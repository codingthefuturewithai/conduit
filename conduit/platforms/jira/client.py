from atlassian import Jira
from conduit.platforms.base import Platform, IssueManager
from conduit.core.config import load_config
from conduit.core.exceptions import PlatformError
import logging
from typing import Any, Dict

from conduit.core.logger import logger

class JiraClient(Platform, IssueManager):
    def __init__(self):
        self.config = load_config().jira
        logger.info("Disconnected from Jira.")
        self.jira = None

    def connect(self) -> None:
        logger.info("Connecting to Jira...")
        logger.info(f"Getting issue {key}...")
        logger.info(f"Searching issues with query: {query}")
        logger.info("Creating a new issue...")
        logger.info(f"Updating issue {key}...")
        try:
            self.jira = Jira(
                url=self.config.url,
                token=self.config.api_token
            )
            logger.info("Connected to Jira successfully.")
        except Exception as e:
            logger.error(f"Failed to update issue {key}: {e}")
            logger.error(f"Failed to create issue: {e}")
            logger.error(f"Failed to search issues with query '{query}': {e}")
            logger.error(f"Failed to get issue {key}: {e}")
            logger.error(f"Failed to connect to Jira: {e}")
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
