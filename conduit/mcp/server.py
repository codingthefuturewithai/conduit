"""MCP server implementation for Conduit"""

from typing import Dict, List, Optional
from mcp.server.fastmcp import FastMCP, Context
import mcp.types as types
import logging
import json
import sys
from urllib.parse import unquote
import asyncio
import os

from conduit.core.services import ConfigService, ConfluenceService
from conduit.core.config import load_config

# Configure ALL logging to write to stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.WARNING,  # Default to WARNING to reduce noise
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Get loggers but keep them quiet by default
logger = logging.getLogger("conduit.mcp")
mcp_logger = logging.getLogger("mcp.server")
uvicorn_logger = logging.getLogger("uvicorn")
root_logger = logging.getLogger()

# Remove any existing handlers to ensure clean stderr-only logging
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add stderr handler to root logger
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
root_logger.addHandler(stderr_handler)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server instance"""
    # Get port from environment or use default
    port = int(os.environ.get("MCP_PORT", "8000"))

    # Create the server instance with minimal logging
    mcp = FastMCP(
        "Conduit",
        host="localhost",
        port=port,
        debug=False,  # Reduce debug noise
        log_level="WARNING",  # Keep FastMCP quiet too
    )
    return mcp


# Create initial server instance
mcp = create_mcp_server()


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
async def get_confluence_page(
    space_key: str, title: str, site_alias: Optional[str] = None
) -> list[types.TextContent]:
    """Get Confluence page content by title within a space"""
    try:
        logger.debug(
            f"Executing get_confluence_page for page '{title}' in space {space_key} with site {site_alias}"
        )
        # Get the Confluence client from the registry
        from conduit.platforms.registry import PlatformRegistry

        client = PlatformRegistry.get_platform("confluence", site_alias=site_alias)
        client.connect()

        # Get page using the client
        page = client.get_page_by_title(space_key, title)
        if not page:
            raise ValueError(f"Page '{title}' not found in space {space_key}")

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
            f"get_confluence_page formatted {len(markdown)} characters of content as markdown"
        )
        return [types.TextContent(type="text", text=markdown)]
    except Exception as e:
        logger.error(f"Error in get_confluence_page: {e}", exc_info=True)
        raise


@mcp.tool()
async def search_jira_issues(
    query: str, site_alias: Optional[str] = None
) -> list[types.TextContent]:
    """Search Jira issues using JQL syntax"""
    try:
        logger.debug(
            f"Executing search_jira_issues tool with query '{query}' and site {site_alias}"
        )
        # Get the Jira client from the registry
        from conduit.platforms.registry import PlatformRegistry

        client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
        client.connect()

        # Search using the client
        results = client.search(query)
        logger.debug(f"search_jira_issues found {len(results)} issues")
        return [types.TextContent(type="text", text=str(results))]
    except Exception as e:
        logger.error(f"Error in search_jira_issues: {e}", exc_info=True)
        raise


@mcp.tool()
async def create_jira_issue(
    project: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    site_alias: Optional[str] = None,
) -> list[types.TextContent]:
    """Create a new Jira issue"""
    try:
        logger.debug(
            f"Executing create_jira_issue tool for project '{project}' with type '{issue_type}' and site {site_alias}"
        )
        # Get the Jira client from the registry
        from conduit.platforms.registry import PlatformRegistry

        client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
        client.connect()

        # Create the issue using the client with proper field structure
        result = client.create(
            project={"key": project},
            summary=summary,
            description=description,
            issuetype={"name": issue_type},
        )
        logger.debug(f"create_jira_issue created issue: {result}")
        return [types.TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Error in create_jira_issue: {e}", exc_info=True)
        raise


@mcp.tool()
async def update_jira_issue(
    key: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    site_alias: Optional[str] = None,
) -> list[types.TextContent]:
    """Update an existing Jira issue"""
    try:
        logger.debug(
            f"Executing update_jira_issue tool for issue '{key}' with site {site_alias}"
        )
        # Get the Jira client from the registry
        from conduit.platforms.registry import PlatformRegistry

        client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
        client.connect()

        # Build update fields dictionary with only provided values
        fields = {}
        if summary is not None:
            fields["summary"] = summary
        if description is not None:
            fields["description"] = description

        # Update the issue using the client
        client.update(key, **fields)

        # Get and return the updated issue
        updated_issue = client.get(key)
        logger.debug(f"update_jira_issue updated issue: {updated_issue}")
        return [types.TextContent(type="text", text=str(updated_issue))]
    except Exception as e:
        logger.error(f"Error in update_jira_issue: {e}", exc_info=True)
        raise


@mcp.tool()
async def list_all_confluence_pages(
    space_key: str, batch_size: int = 100, site_alias: Optional[str] = None
) -> list[types.TextContent]:
    """List all pages in a Confluence space with pagination support"""
    try:
        logger.debug(
            f"Executing list_all_confluence_pages tool for space {space_key} with site {site_alias} and batch_size {batch_size}"
        )
        # Get the Confluence client from the registry
        from conduit.platforms.registry import PlatformRegistry

        client = PlatformRegistry.get_platform("confluence", site_alias=site_alias)
        client.connect()

        # Get all pages using pagination
        pages = client.get_all_pages_by_space(space_key, batch_size=batch_size)
        logger.debug(f"list_all_confluence_pages found {len(pages)} pages")

        # Format response as markdown
        markdown_response = f"\nFound {len(pages)} pages in space {space_key}:\n"
        for page in pages:
            markdown_response += f"- {page.get('title')} (ID: {page.get('id')})\n"

        return [types.TextContent(type="text", text=markdown_response)]
    except Exception as e:
        logger.error(f"Error in list_all_confluence_pages: {e}", exc_info=True)
        raise
