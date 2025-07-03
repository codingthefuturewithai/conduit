from typing import Dict, List, Optional
import re

from conduit.core.config import load_config
from conduit.core.logger import logger
from conduit.platforms.confluence.client import ConfluenceClient


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
        attachments: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        """Create a new Confluence page from markdown content

        Args:
            space_key: The key of the Confluence space
            title: The title of the page to create
            content: Markdown content for the page
            parent_id: Optional ID of the parent page
            site_alias: Optional site alias for multi-site configurations
            attachments: Optional list of attachments to upload
                Each attachment dict should have:
                - local_path: Path to the file on local filesystem
                - name_on_confluence: Name for the attachment on Confluence

        Returns:
            Dict containing the created page information
        """
        # Get client and configuration
        client = cls._get_client(site_alias)
        confluence_config = client.config
        site_config = confluence_config.get_site_config(site_alias)
        client.connect()  # Ensure we're connected

        # Pre-process markdown to normalize image paths before md2cf conversion
        import re
        processed_content = content
        
        if attachments:
            # Build a mapping of filenames to their attachment names
            attachment_filenames = [att.get("name_on_confluence", "") for att in attachments if att.get("name_on_confluence")]
            
            # Replace any image references that point to files we're attaching
            # This handles both full paths and relative paths
            for att in attachments:
                local_path = att.get("local_path", "")
                confluence_name = att.get("name_on_confluence", "")
                if local_path and confluence_name:
                    # Replace full path references with just the filename
                    # This ensures md2cf will treat them as attachments
                    processed_content = processed_content.replace(f']({local_path})', f']({confluence_name})')
                    # Also handle cases where the path might be quoted
                    processed_content = processed_content.replace(f']("{local_path}")', f']({confluence_name})')
                    processed_content = processed_content.replace(f"]'{local_path}')", f']({confluence_name})')
            
            logger.info(f"Pre-processed markdown to normalize {len(attachments)} image paths")
        
        # Convert markdown to Confluence storage format using md2cf
        import mistune
        from md2cf.confluence_renderer import ConfluenceRenderer

        # Create renderer with use_xhtml=True to properly handle images
        renderer = ConfluenceRenderer(use_xhtml=True)
        markdown_parser = mistune.Markdown(renderer=renderer)
        confluence_content = markdown_parser(processed_content)
        
        # Log any attachments that md2cf found
        if renderer.attachments:
            logger.info(f"md2cf found {len(renderer.attachments)} images to attach: {renderer.attachments}")

        # Create the page using the client's API with storage representation
        response = await client.create_page(
            space_key=space_key,
            title=title,
            body=confluence_content,
            parent_id=parent_id,
            representation="storage",  # Use storage representation for converted content
        )

        page_id = response.get("id")

        # Attach files if provided
        if attachments and page_id:
            logger.info(f"Attaching {len(attachments)} file(s) to page {page_id}")
            for attachment in attachments:
                try:
                    local_path = attachment.get("local_path")
                    name_on_confluence = attachment.get("name_on_confluence")

                    if not local_path or not name_on_confluence:
                        logger.warning(f"Skipping invalid attachment: {attachment}")
                        continue

                    client.attach_file(
                        page_id=page_id,
                        file_path=local_path,
                        attachment_name=name_on_confluence,
                    )
                    logger.info(f"Successfully attached {name_on_confluence}")
                except Exception as e:
                    logger.error(f"Failed to attach file {attachment}: {e}")
                    # Continue with other attachments even if one fails

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
        attachments: Optional[List[Dict[str, str]]] = None,
    ) -> Dict:
        """Update an existing Confluence page with new markdown content

        Args:
            space_key: The key of the Confluence space
            title: The title of the page to update
            content: New markdown content for the page
            expected_version: The version number we expect the page to be at
            site_alias: Optional site alias for multi-site configurations
            minor_edit: Whether this is a minor edit (to avoid notification spam)
            attachments: Optional list of attachments to upload
                Each attachment dict should have:
                - local_path: Path to the file on local filesystem
                - name_on_confluence: Name for the attachment on Confluence

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

        page_id = current_page["id"]

        # Build list of attachment filenames FIRST (before attaching)
        attachment_filenames = []
        if attachments:
            attachment_filenames = [att.get("name_on_confluence", "") for att in attachments if att.get("name_on_confluence")]
            
        # Attach files if provided
        if attachments:
            logger.info(f"Attaching {len(attachments)} file(s) to page {page_id}")
            for attachment in attachments:
                try:
                    local_path = attachment.get("local_path")
                    name_on_confluence = attachment.get("name_on_confluence")

                    if not local_path or not name_on_confluence:
                        logger.warning(f"Skipping invalid attachment: {attachment}")
                        continue

                    client.attach_file(
                        page_id=page_id,
                        file_path=local_path,
                        attachment_name=name_on_confluence,
                    )
                    logger.info(f"Successfully attached {name_on_confluence}")
                except Exception as e:
                    logger.error(f"Failed to attach file {attachment}: {e}")
                    # Continue with other attachments even if one fails

        # Pre-process markdown to normalize image paths before md2cf conversion
        import re
        processed_content = content
        
        if attachments:
            # Build a mapping of filenames to their attachment names
            attachment_filenames = [att.get("name_on_confluence", "") for att in attachments if att.get("name_on_confluence")]
            
            # Replace any image references that point to files we're attaching
            # This handles both full paths and relative paths
            for att in attachments:
                local_path = att.get("local_path", "")
                confluence_name = att.get("name_on_confluence", "")
                if local_path and confluence_name:
                    # Replace full path references with just the filename
                    # This ensures md2cf will treat them as attachments
                    processed_content = processed_content.replace(f']({local_path})', f']({confluence_name})')
                    # Also handle cases where the path might be quoted
                    processed_content = processed_content.replace(f']("{local_path}")', f']({confluence_name})')
                    processed_content = processed_content.replace(f"]'{local_path}')", f']({confluence_name})')
            
            logger.info(f"Pre-processed markdown to normalize {len(attachments)} image paths")
        
        # Convert markdown to Confluence storage format using md2cf
        import mistune
        from md2cf.confluence_renderer import ConfluenceRenderer

        # Create renderer with use_xhtml=True to properly handle images
        renderer = ConfluenceRenderer(use_xhtml=True)
        markdown_parser = mistune.Markdown(renderer=renderer)
        confluence_content = markdown_parser(processed_content)
        
        # Log any attachments that md2cf found
        if renderer.attachments:
            logger.info(f"md2cf found {len(renderer.attachments)} images to attach: {renderer.attachments}")

        # Update the page using the client's update_page method
        response = client.confluence.update_page(
            page_id=page_id,
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
