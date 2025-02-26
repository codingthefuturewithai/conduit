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
        page_id = await client.create_page(
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
            "id": page_id,
            "title": title,
            "space_key": space_key,
            "url": f"https://{domain}/wiki/spaces/{space_key}/pages/{page_id}",
        }

    @classmethod
    async def create_page_from_markdown_direct(
        cls,
        space_key: str,
        title: str,
        content: str,
        parent_id: Optional[str] = None,
        site_alias: Optional[str] = None,
        update: bool = True,
        minor_edit: bool = False,
        version_comment: str = "Updated via Conduit",
    ) -> Dict:
        """Create a new Confluence page from markdown content using md2cf's MinimalConfluence

        This method uses the MinimalConfluence class from md2cf directly, bypassing the
        Conduit client. This can be useful for users who want to use the md2cf library directly.

        Args:
            space_key: The key of the Confluence space
            title: The title of the page to create
            content: Markdown content for the page
            parent_id: Optional ID of the parent page
            site_alias: Optional site alias for multi-site configurations
            update: Whether to update the page if it already exists
            minor_edit: Whether this is a minor edit
            version_comment: Comment for the version history

        Returns:
            Dict containing the created page information
        """
        # Get client and configuration
        client = cls._get_client(site_alias)
        confluence_config = client.config
        site_config = confluence_config.get_site_config(site_alias)

        # Import md2cf components
        from md2cf.api import MinimalConfluence
        from md2cf.confluence_renderer import ConfluenceRenderer
        import mistune

        # Convert markdown to Confluence storage format
        renderer = ConfluenceRenderer()
        markdown_parser = mistune.Markdown(renderer=renderer)
        confluence_content = markdown_parser(content)

        # Initialize MinimalConfluence client
        confluence = MinimalConfluence(
            host=f"{site_config.url}/rest/api",
            username=site_config.email,
            password=site_config.api_token,
        )

        # Create or update the page
        response = confluence.create_page(
            space=space_key,
            title=title,
            body=confluence_content,
            parent_id=parent_id,
            update=update,
            minor_edit=minor_edit,
            version_comment=version_comment,
        )

        # Extract domain from URL for the return URL
        domain = (
            site_config.url.replace("https://", "").replace("http://", "").split("/")[0]
        )

        # Return the created page details
        return {
            "id": response.get("id"),
            "title": response.get("title"),
            "space_key": space_key,
            "url": f"https://{domain}/wiki/spaces/{space_key}/pages/{response.get('id')}",
            "version": response.get("version", {}).get("number"),
            "response": response,
        }
