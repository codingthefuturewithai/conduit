from typing import Dict, List, Optional, Any
from atlassian import Confluence

from conduit.core.config import load_config
from conduit.core.logger import logger
from conduit.core.exceptions import ConfigurationError, PlatformError
from conduit.platforms.base import Platform
from conduit.platforms.confluence.content import ConfluenceContentCleaner


class ConfluenceClient(Platform):
    """Client for interacting with Confluence."""

    def __init__(self, site_alias: Optional[str] = None):
        try:
            self.config = load_config().confluence
            self.site_config = self.config.get_site_config(site_alias)
            self.confluence = None
            self.content_cleaner = ConfluenceContentCleaner()
            logger.info(
                f"Initialized Confluence client for site: {site_alias or 'default'}"
            )
        except (FileNotFoundError, ConfigurationError) as e:
            logger.error(f"Failed to initialize Confluence client: {e}")
            raise

    def connect(self) -> None:
        """Connect to Confluence using configuration settings."""
        logger.info("Connecting to Confluence...")
        try:
            if not self.confluence:
                self.confluence = Confluence(
                    url=self.site_config.url,
                    username=self.site_config.email,
                    password=self.site_config.api_token,
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

    def get_space_content(
        self,
        space_key: str,
        depth: str = "all",
        start: int = 0,
        limit: int = 500,
        expand: str = "body.storage",
        format: str = "storage",
    ) -> Dict[str, Any]:
        """
        Get space content with expanded details including body content.

        Args:
            space_key: The key of the space to get content from
            depth: Depth of the content tree to return (default: "all")
            start: Start index for pagination (default: 0)
            limit: Maximum number of items to return (default: 500)
            expand: Comma-separated list of properties to expand (default: "body.storage")
            format: Content format to return (default: "storage")
                   - "storage": Raw Confluence storage format
                   - "clean": Cleaned text with minimal formatting

        Returns:
            Dictionary containing space content with expanded details

        Raises:
            PlatformError: If the operation fails
            ValueError: If an invalid format is specified
        """
        if format not in ["storage", "clean"]:
            raise ValueError('format must be either "storage" or "clean"')

        if not self.confluence:
            raise PlatformError("Not connected to Confluence")

        try:
            logger.info(f"Getting content for space: {space_key}")
            logger.debug(f"Using expand parameters: {expand}")

            content = self.confluence.get_space_content(
                space_key,
                depth=depth,
                start=start,
                limit=limit,
                expand=expand,
            )

            # If clean format requested, process the content
            if format == "clean" and content.get("page", {}).get("results"):
                for page in content["page"]["results"]:
                    if "body" in page and "storage" in page["body"]:
                        page["body"]["clean"] = self.content_cleaner.clean(
                            page["body"]["storage"]["value"]
                        )

            logger.info(f"Successfully retrieved content for space {space_key}")
            return content

        except Exception as e:
            logger.error(f"Failed to get content for space {space_key}: {e}")
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise PlatformError(f"Failed to get content for space {space_key}: {e}")

    def get_page_by_title(
        self, space_key: str, title: str, expand: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a Confluence page by its title within a specific space.

        Args:
            space_key: The key of the space containing the page
            title: The title of the page to retrieve
            expand: Optional comma-separated list of properties to expand

        Returns:
            Dictionary containing page details if found, None if not found

        Raises:
            PlatformError: If the operation fails
        """
        if not self.confluence:
            raise PlatformError("Not connected to Confluence")

        try:
            logger.info(f"Getting page by title '{title}' in space: {space_key}")
            logger.debug(f"Using expand parameters: {expand}")

            page = self.confluence.get_page_by_title(
                space=space_key,
                title=title,
                expand=expand or "version,body.storage",
            )

            if page:
                logger.info(f"Found page: {page.get('id')} - {page.get('title')}")
                logger.debug(f"Page details: {page}")
                return page
            else:
                logger.info(f"No page found with title '{title}' in space {space_key}")
                return None

        except Exception as e:
            logger.error(f"Failed to get page '{title}' in space {space_key}: {e}")
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise PlatformError(
                f"Failed to get page '{title}' in space {space_key}: {e}"
            )
