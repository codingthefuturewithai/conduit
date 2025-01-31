from typing import Dict, List, Optional, Any
from atlassian import Confluence

from conduit.core.config import load_config
from conduit.core.logger import logger
from conduit.core.exceptions import ConfigurationError, PlatformError
from conduit.platforms.base import Platform


class ConfluenceClient(Platform):
    """Client for interacting with Confluence."""

    def __init__(self):
        try:
            self.config = load_config().confluence
            self.confluence = None
            logger.info("Initialized Confluence client")
        except (FileNotFoundError, ConfigurationError) as e:
            logger.error(f"Failed to initialize Confluence client: {e}")
            raise

    def connect(self) -> None:
        """Connect to Confluence using configuration settings."""
        logger.info("Connecting to Confluence...")
        try:
            if not self.confluence:
                self.confluence = Confluence(
                    url=self.config.url,
                    username=self.config.email,
                    password=self.config.api_token,
                    cloud=True,
                )
                logger.info("Connected to Confluence successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Confluence: {e}")
            raise PlatformError(f"Failed to connect to Confluence: {e}")

    def disconnect(self) -> None:
        """Disconnect from Confluence."""
        self.confluence = None
        logger.info("Disconnected from Confluence.")

    def get_pages_by_space(
        self, space_key: str, limit: int = 100, expand: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get pages in a given space with a limit.

        Args:
            space_key: The key of the space to get pages from
            limit: Maximum number of pages to return (default: 100)
            expand: Optional comma-separated list of properties to expand

        Returns:
            List of pages with their details

        Raises:
            PlatformError: If the operation fails
        """
        if not self.confluence:
            raise PlatformError("Not connected to Confluence")

        try:
            logger.info(f"Getting pages for space: {space_key}")
            logger.debug(f"Using expand parameters: {expand}")

            pages = self.confluence.get_all_pages_from_space(
                space=space_key,
                start=0,
                limit=limit,
                content_type="page",
                expand=expand or "version,body.storage",
            )

            logger.info(f"Found {len(pages)} pages in space {space_key}")
            logger.debug(f"First page details: {pages[0] if pages else None}")

            return pages
        except Exception as e:
            logger.error(f"Failed to get pages for space {space_key}: {e}")
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise PlatformError(f"Failed to get pages for space {space_key}: {e}")

    def get_all_pages_by_space(
        self, space_key: str, expand: Optional[str] = None, batch_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all pages in a given space using pagination.

        Args:
            space_key: The key of the space to get pages from
            expand: Optional comma-separated list of properties to expand
            batch_size: Number of pages to fetch per request (default: 100)

        Returns:
            List of all pages with their details

        Raises:
            PlatformError: If the operation fails
        """
        if not self.confluence:
            raise PlatformError("Not connected to Confluence")

        try:
            logger.info(f"Getting all pages for space: {space_key}")
            logger.debug(f"Using expand parameters: {expand}")

            all_pages = []
            start = 0

            while True:
                logger.debug(f"Fetching pages starting at offset: {start}")
                pages = self.confluence.get_all_pages_from_space(
                    space=space_key,
                    start=start,
                    limit=batch_size,
                    content_type="page",
                    expand=expand or "version,body.storage",
                )

                if not pages:
                    break

                all_pages.extend(pages)
                start += len(pages)

                if len(pages) < batch_size:
                    break

            logger.info(f"Found total of {len(all_pages)} pages in space {space_key}")
            return all_pages

        except Exception as e:
            logger.error(f"Failed to get all pages for space {space_key}: {e}")
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise PlatformError(f"Failed to get all pages for space {space_key}: {e}")

    def get_child_pages(
        self, parent_id: str, limit: int = 100, expand: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all child pages of a given parent page.

        Args:
            parent_id: The ID of the parent page
            limit: Maximum number of pages to return (default: 100)
            expand: Optional comma-separated list of properties to expand

        Returns:
            List of child pages with their details

        Raises:
            PlatformError: If the operation fails
        """
        if not self.confluence:
            raise PlatformError("Not connected to Confluence")

        try:
            logger.info(f"Getting child pages for parent ID: {parent_id}")
            logger.debug(f"Using expand parameters: {expand}")

            pages = self.confluence.get_page_child_by_type(
                page_id=parent_id, type="page", start=0, limit=limit, expand=expand
            )

            logger.info(f"Found {len(pages)} child pages for parent {parent_id}")
            logger.debug(f"First child page details: {pages[0] if pages else None}")

            return pages
        except Exception as e:
            logger.error(f"Failed to get child pages for parent {parent_id}: {e}")
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise PlatformError(
                f"Failed to get child pages for parent {parent_id}: {e}"
            )
