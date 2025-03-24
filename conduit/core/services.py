from typing import Dict, List, Optional

from conduit.core.config import Config, load_config
from conduit.platforms.confluence.client import ConfluenceClient
from conduit.platforms.confluence.config import ConfluenceConfig


class ConfigService:
    """Service layer for configuration operations"""

    @classmethod
    def list_configs(cls) -> Dict:
        """List all configured sites for both Jira and Confluence"""
        config = load_config()
        return {
            "jira": config.jira.dict(),
            "confluence": config.confluence.dict(),
        }


class ConfluenceService:
    """Service layer for Confluence operations"""

    @classmethod
    def _get_client(cls, site_alias: Optional[str] = None) -> ConfluenceClient:
        # Just pass the site_alias to the client constructor
        # The client will load the config internally
        return ConfluenceClient(site_alias)

    @classmethod
    async def list_pages(
        cls, space_key: str, site_alias: Optional[str] = None
    ) -> List[Dict]:
        """List all pages in a Confluence space"""
        client = cls._get_client(site_alias)
        return await client.list_pages(space_key)

    @classmethod
    async def get_page(
        cls, space_key: str, page_title: str, site_alias: Optional[str] = None
    ) -> Dict:
        """Get a specific Confluence page by space and title"""
        client = cls._get_client(site_alias)
        return await client.get_page_by_title(space_key, page_title)

    @classmethod
    async def create_page_from_markdown(
        cls,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None,
        site_alias: Optional[str] = None,
    ) -> Dict:
        """Create a new Confluence page from markdown content

        Args:
            space_key: The key of the Confluence space
            title: The title of the page to create
            content: Markdown content for the page
            parent_id: Optional ID of the parent page
            site_alias: Optional site alias for multi-site configurations

        Returns:
            Dict containing the created page information
        """
        # Get client and configuration
        client = cls._get_client(site_alias)
        confluence_config = client.config
        site_config = confluence_config.get_site_config(site_alias)

        # Convert markdown to Confluence storage format using md2cf
        from md2cf.confluence_renderer import ConfluenceRenderer
        import mistune

        # Convert Markdown to Confluence Storage Format
        renderer = ConfluenceRenderer()
        markdown_parser = mistune.Markdown(renderer=renderer)
        confluence_content = markdown_parser(content)

        # Create the page using the client's API with storage representation
        response = await client.create_page(
            space_key=space_key,
            title=title,
            body=confluence_content,
            parent_id=parent_id,
            representation="storage",  # Use storage representation for converted content
        )

        # Extract domain from URL for the return URL
        domain = (
            site_config.url.replace("https://", "").replace("http://", "").split("/")[0]
        )

        # Return the created page details
        return {
            "id": response.get("id"),
            "title": title,
            "space_key": space_key,
            "url": f"https://{domain}/wiki/spaces/{space_key}/pages/{response.get('id')}",
            "version": response.get("version", {}).get("number", 1),
            "response": response,  # Include full response for additional details
        }

    @classmethod
    async def update_page_from_markdown(
        cls,
        space_key: str,
        title: str,
        content: str,
        expected_version: int,
        site_alias: Optional[str] = None,
        minor_edit: bool = False,
    ) -> Dict:
        """Update an existing Confluence page with new markdown content

        Args:
            space_key: The key of the Confluence space
            title: The title of the page to update
            content: New markdown content for the page
            expected_version: The version number we expect the page to be at
            site_alias: Optional site alias for multi-site configurations
            minor_edit: Whether this is a minor edit (to avoid notification spam)

        Returns:
            Dict containing the updated page information

        Raises:
            ValueError: If page doesn't exist or version mismatch
            PlatformError: If update fails
        """
        # Get client and check current version
        client = cls._get_client(site_alias)
        client.connect()  # Ensure we're connected

        # Get the current page
        current_page = client.get_page_by_title(space_key, title)
        if not current_page:
            raise ValueError(f"Page '{title}' not found in space {space_key}")

        current_version = current_page.get("version", {}).get("number")
        if current_version != expected_version:
            raise ValueError(
                f"Version mismatch: expected {expected_version}, but page is at version {current_version}"
            )

        # Convert markdown to Confluence storage format using md2cf
        from md2cf.confluence_renderer import ConfluenceRenderer
        import mistune

        renderer = ConfluenceRenderer()
        markdown_parser = mistune.Markdown(renderer=renderer)
        confluence_content = markdown_parser(content)

        # Update the page using the client's update_page method
        response = client.confluence.update_page(
            page_id=current_page["id"],
            title=title,
            body=confluence_content,
            type="page",
            representation="storage",
            minor_edit=minor_edit,
        )

        # Extract domain from URL for the return URL
        site_config = client.config.get_site_config(site_alias)
        domain = (
            site_config.url.replace("https://", "").replace("http://", "").split("/")[0]
        )

        # Return consistent response format
        return {
            "id": response.get("id"),
            "title": response.get("title"),
            "space_key": space_key,
            "url": f"https://{domain}/wiki/spaces/{space_key}/pages/{response.get('id')}",
            "version": response.get("version", {}).get("number"),
            "response": response,
        }
