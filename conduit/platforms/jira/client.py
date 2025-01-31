from atlassian import Jira
from conduit.platforms.base import Platform, IssueManager
from conduit.core.config import load_config
from conduit.core.exceptions import ConfigurationError, PlatformError
import logging
from typing import Any, Dict, Optional, List

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
                    username=self.config.email,
                    password=self.config.api_token,
                    cloud=True,
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
            return issue.raw if hasattr(issue, "raw") else issue
        except Exception as e:
            raise PlatformError(f"Failed to get issue {key}: {e}")

    def search(self, query: str) -> list[Dict[str, Any]]:
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            result = self.jira.jql(query)
            if not result or "issues" not in result:
                return []
            return result["issues"]
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            raise PlatformError(
                f"Failed to search issues with query '{query}': {str(e)}"
            )

    def create(self, **kwargs) -> Dict[str, Any]:
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            fields = {
                "project": {"key": kwargs["project"]["key"]},
                "summary": kwargs["summary"],
                "description": kwargs.get("description", ""),
                "issuetype": {"name": kwargs.get("issuetype", {}).get("name", "Task")},
            }
            logger.info(f"Creating issue with fields: {fields}")
            logger.info(f"Jira API URL: {self.config.url}")
            logger.info(f"API Token length: {len(self.config.api_token)}")

            try:
                logger.info("Making API call to create issue...")
                result = self.jira.issue_create(fields=fields)
                logger.info(f"API Response: {result}")
            except Exception as api_error:
                logger.error(f"API Error details: {str(api_error)}")
                logger.error(f"API Error type: {type(api_error)}")
                if hasattr(api_error, "response"):
                    logger.error(f"Response status: {api_error.response.status_code}")
                    logger.error(f"Response body: {api_error.response.text}")
                raise

            if not result:
                raise PlatformError("No response from Jira API")
            return result
        except Exception as e:
            logger.error(f"Create error: {str(e)}")
            raise PlatformError(f"Failed to create issue: {str(e)}")

    def update(self, key: str, **kwargs) -> None:
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            fields = {k: v for k, v in kwargs.items() if v is not None}
            if not fields:
                return
            logger.debug(f"Updating issue {key} with fields: {fields}")
            self.jira.issue_update(key, fields)
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            raise PlatformError(f"Failed to update issue {key}: {str(e)}")

    def get_transitions(self, key: str) -> List[Dict[str, Any]]:
        """Get available transitions for an issue."""
        if not self.jira:
            raise PlatformError("Not connected to Jira")
        try:
            transitions = self.jira.get_issue_transitions(key)
            logger.debug(f"Raw transitions response: {transitions}")
            return transitions
        except Exception as e:
            logger.error(f"Failed to get transitions for issue {key}: {e}")
            raise PlatformError(f"Failed to get transitions for issue {key}: {e}")

    def transition_status(self, key: str, status: str) -> None:
        """
        Transition an issue to a new status.

        Args:
            key: The issue key (e.g., 'PROJ-123')
            status: The target status name (e.g., 'In Progress')

        Raises:
            PlatformError: If the transition fails or the status is invalid
        """
        if not self.jira:
            raise PlatformError("Not connected to Jira")

        try:
            # Get current status
            current_status = self.jira.get_issue_status(key)
            logger.info(f"Current status: {current_status}")

            # Get available transitions
            transitions = self.jira.get_issue_transitions(key)
            logger.info("Available transitions:")
            for t in transitions:
                logger.info(f"ID: {t['id']}, Name: {t['name']}")

            # Try to set the status directly
            logger.info(f"Setting issue {key} status to '{status}'")
            self.jira.set_issue_status(key, status)
            logger.info(f"Successfully set issue {key} status to '{status}'")

        except PlatformError:
            raise
        except Exception as e:
            logger.error(f"Failed to transition issue {key} to status '{status}': {e}")
            raise PlatformError(
                f"Failed to transition issue {key} to status '{status}': {e}"
            )
