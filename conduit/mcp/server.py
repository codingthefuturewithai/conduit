"""MCP server implementation for Conduit"""

from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP, Context
import mcp.types as types
import logging
import json
import sys
from urllib.parse import unquote

from conduit.core.services import ConfigService, ConfluenceService
from conduit.core.config import load_config

# Configure logging to write to stderr instead of a file
logging.basicConfig(
    stream=sys.stderr,  # Write to stderr instead of a file
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Get all relevant loggers
logger = logging.getLogger("conduit.mcp")
mcp_logger = logging.getLogger("mcp.server")
root_logger = logging.getLogger()

# Remove any existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add stderr handler to root logger
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stderr_handler.setFormatter(formatter)
root_logger.addHandler(stderr_handler)

# Create the server instance
mcp = FastMCP("Conduit")


@mcp.tool()
async def list_config() -> list[types.TextContent]:
    """List all configured Jira and Confluence sites"""
    try:
        logger.debug("Executing list_config tool")
        config = load_config()

        config_dict = {
            "jira": {
                "default_site_alias": config.jira.default_site_alias,
                "sites": {
                    alias: {"url": site.url, "email": site.email, "api_token": "****"}
                    for alias, site in config.jira.sites.items()
                },
            },
            "confluence": {
                "default_site_alias": config.confluence.default_site_alias,
                "sites": {
                    alias: {"url": site.url, "email": site.email, "api_token": "****"}
                    for alias, site in config.confluence.sites.items()
                },
            },
        }

        logger.debug(f"list_config result: {config_dict}")
        return [types.TextContent(type="text", text=str(config_dict))]
    except Exception as e:
        logger.error(f"Error in list_config: {e}", exc_info=True)
        raise


@mcp.tool()
async def list_confluence_pages(
    space_key: str, site_alias: Optional[str] = None
) -> list[types.TextContent]:
    """List all pages in a Confluence space"""
    try:
        logger.debug(
            f"Executing list_confluence_pages tool for space {space_key} with site {site_alias}"
        )
        # Get the Confluence client from the registry
        from conduit.platforms.registry import PlatformRegistry

        client = PlatformRegistry.get_platform("confluence", site_alias=site_alias)
        client.connect()

        # Get pages using the client
        pages = client.get_pages_by_space(space_key)
        logger.debug(f"list_confluence_pages found {len(pages)} pages")
        return [types.TextContent(type="text", text=str(pages))]
    except Exception as e:
        logger.error(f"Error in list_confluence_pages: {e}", exc_info=True)
        raise


@mcp.resource("confluence://{space_key}/{page_title}?site={site}")
async def get_confluence_page_resource(
    space_key: str, page_title: str, site: Optional[str] = None
) -> str:
    """Get Confluence page content as a resource"""
    try:
        # URL decode the page title
        decoded_title = unquote(page_title).rstrip("?")

        logger.debug(
            f"Executing get_confluence_page_resource for page '{decoded_title}' in space {space_key} with site {site}"
        )
        # Get the Confluence client from the registry
        from conduit.platforms.registry import PlatformRegistry

        client = PlatformRegistry.get_platform("confluence", site_alias=site)
        client.connect()

        # Get page using the client
        page = client.get_page_by_title(space_key, decoded_title)
        if not page:
            raise ValueError(f"Page '{decoded_title}' not found in space {space_key}")

        # Get the raw content and clean it
        raw_content = page.get("body", {}).get("storage", {}).get("value", "")
        clean_content = client.content_cleaner.clean(raw_content)

        # Process the clean content to improve table formatting
        lines = clean_content.split("\n")
        formatted_lines = []
        in_table = False

        for line in lines:
            # Detect table header separator and format it properly
            if line.startswith("---------"):
                in_table = True
                # Count the number of columns from the previous line
                prev_line = formatted_lines[-1] if formatted_lines else ""
                num_columns = prev_line.count("|") + 1
                formatted_lines.append("|" + " --- |" * num_columns)
                continue

            # Add proper spacing around headings
            if line.startswith("**") and line.endswith("**"):
                formatted_lines.extend(["", line, ""])
                continue

            # Ensure table rows have proper spacing
            if "|" in line:
                in_table = True
                # Clean up table row formatting
                cells = [cell.strip() for cell in line.split("|")]
                formatted_lines.append("| " + " | ".join(cells) + " |")
                continue

            # Add extra line break after table
            if in_table and not line.strip():
                in_table = False
                formatted_lines.extend(["", ""])
                continue

            formatted_lines.append(line)

        # Build the markdown content parts separately
        title_section = f"# {page['title']}"
        details_section = (
            "**Page Details:**\n"
            f"- ID: {page['id']}\n"
            f"- Version: {page.get('version', {}).get('number', 'Unknown')}\n"
            f"- Last Updated: {page.get('version', {}).get('when', 'Unknown')}"
        )
        content_section = "**Content:**"
        formatted_content = "\n".join(formatted_lines)

        # Combine all sections with proper spacing
        markdown = f"{title_section}\n\n{details_section}\n\n{content_section}\n{formatted_content}"

        logger.debug(
            f"get_confluence_page_resource formatted {len(markdown)} characters of content as markdown"
        )
        return markdown
    except Exception as e:
        logger.error(f"Error in get_confluence_page_resource: {e}", exc_info=True)
        raise


def main():
    """Entry point for MCP server"""
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
