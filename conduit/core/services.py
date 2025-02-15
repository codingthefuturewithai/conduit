from typing import Dict, List, Optional

from conduit.core.config import Config
from conduit.platforms.confluence.client import ConfluenceClient
from conduit.platforms.confluence.config import ConfluenceConfig


class ConfigService:
    """Service layer for configuration operations"""

    @classmethod
    def list_configs(cls) -> Dict:
        """List all configured sites for both Jira and Confluence"""
        config = Config()
        return {
            "jira": config.get_jira_config().dict(),
            "confluence": config.get_confluence_config().dict(),
        }


class ConfluenceService:
    """Service layer for Confluence operations"""

    @classmethod
    def _get_client(cls, site_alias: Optional[str] = None) -> ConfluenceClient:
        config = Config()
        confluence_config = config.get_confluence_config()
        return ConfluenceClient(confluence_config, site_alias)

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
