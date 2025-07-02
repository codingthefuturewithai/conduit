from typing import Any, Dict, List, Optional, Union

from atlassian import Confluence

from conduit.core.config import load_config
from conduit.core.exceptions import ConfigurationError, PlatformError
from conduit.core.logger import logger
from conduit.platforms.base import Platform
from conduit.platforms.confluence.config import ConfluenceConfig
from conduit.platforms.confluence.content import ConfluenceContentCleaner


class ConfluenceClient(Platform):
    """Client for interacting with Confluence."""

    def __init__(
        self,
        config_or_site_alias: Optional[Union[ConfluenceConfig, str]] = None,
        site_alias: Optional[str] = None,
    ):
        try:
            # Handle the case where the first parameter is a ConfluenceConfig
            if isinstance(config_or_site_alias, ConfluenceConfig):
                self.config = config_or_site_alias
                self.site_config = self.config.get_site_config(site_alias)
                self.site_alias = site_alias
            # Handle the case where the first parameter is a site_alias string or None
            else:
                self.config = load_config().confluence
                # If site_alias is provided as kwarg, use that, otherwise use first param
                self.site_alias = (
                    site_alias if site_alias is not None else config_or_site_alias
                )
                self.site_config = self.config.get_site_config(self.site_alias)

            self.confluence = None
            self.content_cleaner = ConfluenceContentCleaner()
            logger.info(
                f"Initialized Confluence client for site: {self.site_alias or 'default'}"
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

    async def list_pages(self, space_key: str) -> List[Dict[str, Any]]:
        """
        Asynchronously get pages in a given space.

        Args:
            space_key: The key of the space to get pages from

        Returns:
            List of pages with their details

        Raises:
            PlatformError: If the operation fails
        """
        self.connect()
        return self.get_pages_by_space(space_key)

    async def create_page(
        self,
        space_key: str,
        title: str,
        body: str,
        parent_id: Optional[str] = None,
        representation: str = "storage",
    ) -> Dict[str, Any]:
        """
        Create a new page in Confluence.

        Args:
            space_key: The key of the space to create the page in
            title: The title of the page
            body: The content of the page in Confluence storage format
            parent_id: Optional ID of the parent page
            representation: Content representation format (default: "storage")

        Returns:
            The full page object containing id, title, version, etc.

        Raises:
            PlatformError: If the operation fails
        """
        if not self.confluence:
            self.connect()

        try:
            logger.info(f"Creating page '{title}' in space: {space_key}")

            # Create the page
            page = self.confluence.create_page(
                space=space_key,
                title=title,
                body=body,
                parent_id=parent_id,
                representation=representation,
            )

            logger.info(f"Successfully created page: {page.get('id')} - {title}")
            logger.debug(f"Page details: {page}")

            return page

        except Exception as e:
            logger.error(f"Failed to create page '{title}' in space {space_key}: {e}")
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise PlatformError(
                f"Failed to create page '{title}' in space {space_key}: {e}"
            )

    def get_page_hierarchy(
        self,
        space_key: str,
        parent_page_id: Optional[str] = None,
        batch_size: int = 100,
        max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get hierarchical structure of Confluence pages.

        Args:
            space_key: The key of the space to retrieve pages from
            parent_page_id: Optional ID of parent page to start from (defaults to space root)
            batch_size: Maximum number of pages to retrieve (default: 100)
            max_depth: Maximum depth to traverse (None for unlimited)

        Returns:
            Dictionary containing hierarchical page structure with metadata

        Raises:
            PlatformError: If the operation fails
        """
        if not self.confluence:
            raise PlatformError("Not connected to Confluence")

        try:
            logger.info(
                f"Getting page hierarchy for space {space_key}, "
                f"parent: {parent_page_id or 'root'}, batch_size: {batch_size}"
            )

            processed_count = 0

            def build_page_node(page: Dict[str, Any]) -> Dict[str, Any]:
                """Build a standardized page node for the hierarchy."""
                return {
                    "id": page.get("id"),
                    "title": page.get("title"),
                    "url": page.get("_links", {}).get("webui", ""),
                    "version": page.get("version", {}).get("number"),
                    "lastUpdated": page.get("version", {}).get("when"),
                    "children": [],
                }

            def get_children_recursive(
                parent_id: str, current_depth: int
            ) -> List[Dict[str, Any]]:
                """Recursively get children of a page."""
                nonlocal processed_count

                # Check if we've hit our limits
                if processed_count >= batch_size:
                    return []
                if max_depth is not None and current_depth >= max_depth:
                    return []

                children = []
                try:
                    # Get child pages
                    child_pages = self.get_child_pages(
                        parent_id,
                        limit=min(100, batch_size - processed_count),
                        expand="version",
                    )

                    for child in child_pages:
                        if processed_count >= batch_size:
                            break

                        node = build_page_node(child)
                        processed_count += 1

                        # Recursively get children
                        node["children"] = get_children_recursive(
                            child["id"], current_depth + 1
                        )

                        children.append(node)

                except Exception as e:
                    logger.warning(f"Failed to get children for page {parent_id}: {e}")

                return children

            # Build the hierarchy
            result = {
                "space_key": space_key,
                "parent_page_id": parent_page_id,
                "batch_size": batch_size,
                "max_depth": max_depth,
                "total_pages": 0,
                "hierarchy": [],
            }

            if parent_page_id:
                # Start from specific parent page
                try:
                    parent_page = self.confluence.get_page_by_id(
                        parent_page_id, expand="version"
                    )
                    root_node = build_page_node(parent_page)
                    processed_count += 1

                    # Get children of the parent
                    root_node["children"] = get_children_recursive(parent_page_id, 1)
                    result["hierarchy"] = [root_node]

                except Exception as e:
                    logger.error(f"Failed to get parent page {parent_page_id}: {e}")
                    raise PlatformError(f"Failed to get parent page: {e}")
            else:
                # Start from space root - get top-level pages
                top_pages = self.get_pages_by_space(
                    space_key, limit=min(100, batch_size), expand="version,ancestors"
                )

                # Filter for root pages (no ancestors)
                root_pages = [p for p in top_pages if not p.get("ancestors", [])]

                for page in root_pages:
                    if processed_count >= batch_size:
                        break

                    node = build_page_node(page)
                    processed_count += 1

                    # Get children
                    node["children"] = get_children_recursive(page["id"], 1)
                    result["hierarchy"].append(node)

            result["total_pages"] = processed_count
            logger.info(f"Retrieved {processed_count} pages in hierarchical structure")

            return result

        except PlatformError:
            raise
        except Exception as e:
            logger.error(f"Failed to get page hierarchy: {e}")
            raise PlatformError(f"Failed to get page hierarchy: {e}")

    def attach_file(
        self,
        page_id: str,
        file_path: str,
        attachment_name: str,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Attach a file to a Confluence page.

        Args:
            page_id: The ID of the page to attach the file to
            file_path: Local path to the file to attach
            attachment_name: Name for the attachment on Confluence
            content_type: Optional MIME type for the file (auto-detected if not provided)

        Returns:
            Dictionary containing attachment metadata from the API response

        Raises:
            PlatformError: If the operation fails
            FileNotFoundError: If the local file doesn't exist
        """
        if not self.confluence:
            raise PlatformError("Not connected to Confluence")

        import mimetypes
        import os

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Local file not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        # Auto-detect content type if not provided
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"

        try:
            logger.info(
                f"Attaching file '{attachment_name}' to page {page_id}, "
                f"content-type: {content_type}"
            )

            # Use the atlassian-python-api's attach_file method
            result = self.confluence.attach_file(
                filename=file_path,
                name=attachment_name,
                page_id=page_id,
                title=None,  # Not needed when page_id is provided
                space=None,  # Not needed when page_id is provided
                comment=None,
            )

            logger.info(f"Successfully attached file: {attachment_name}")
            logger.debug(f"Attachment response: {result}")

            return result

        except Exception as e:
            logger.error(
                f"Failed to attach file '{attachment_name}' to page {page_id}: {e}"
            )
            if hasattr(e, "response"):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise PlatformError(
                f"Failed to attach file '{attachment_name}' to page {page_id}: {e}"
            )
