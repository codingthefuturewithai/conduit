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


def convert_markdown_images_to_storage(content: str, attachment_filenames: List[str]) -> str:
    """Convert markdown image references to Confluence storage format for attachments.
    
    This function converts markdown image syntax ![alt](filename) to Confluence storage
    format ONLY for images that are being attached to the page. External images and
    images not in the attachment list remain as markdown.
    
    Args:
        content: The markdown content containing image references
        attachment_filenames: List of filenames that are being attached
        
    Returns:
        Content with attachment images converted to storage format
    """
    def replace_image(match):
        alt_text = match.group(1)
        image_ref = match.group(2)
        
        # Extract filename from path (handle both simple names and paths)
        filename = image_ref.split('/')[-1]
        
        # Only convert if this filename is in our attachments list
        if filename in attachment_filenames:
            logger.info(f"Converting markdown image '{filename}' to Confluence storage format")
            return f'<ac:image><ri:attachment ri:filename="{filename}" /></ac:image>'
        else:
            # Keep as markdown for external images or non-attached images
            return match.group(0)
    
    # Pattern matches ![alt](src) - alt text can be empty
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, content)


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

        # If we have attachments, convert markdown image references to storage format
        if attachments:
            attachment_filenames = [att.get("name_on_confluence", "") for att in attachments if att.get("name_on_confluence")]
            content = convert_markdown_images_to_storage(content, attachment_filenames)
            logger.info(f"Converted markdown image references for {len(attachment_filenames)} attachments")

        # Convert markdown to Confluence storage format using md2cf
        import mistune
        from md2cf.confluence_renderer import ConfluenceRenderer

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

        # Attach files if provided (before updating content so images can be embedded)
        attachment_filenames = []
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
                    attachment_filenames.append(name_on_confluence)
                except Exception as e:
                    logger.error(f"Failed to attach file {attachment}: {e}")
                    # Continue with other attachments even if one fails

        # If we have attachments, convert markdown image references to storage format
        if attachment_filenames:
            content = convert_markdown_images_to_storage(content, attachment_filenames)
            logger.info(f"Converted markdown image references for {len(attachment_filenames)} attachments")

        # Convert markdown to Confluence storage format using md2cf
        import mistune
        from md2cf.confluence_renderer import ConfluenceRenderer

        renderer = ConfluenceRenderer()
        markdown_parser = mistune.Markdown(renderer=renderer)
        confluence_content = markdown_parser(content)

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
