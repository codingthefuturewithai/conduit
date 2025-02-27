"""MCP server implementation for Conduit"""

from typing import Dict, List, Optional, Union
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.stdio import stdio_server
import mcp.types as types
import logging
import json
import sys
from urllib.parse import unquote
import asyncio
import anyio
import click

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
uvicorn_logger = logging.getLogger("uvicorn")
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

# Enable debug logging for all relevant loggers
logger.setLevel(logging.DEBUG)
mcp_logger.setLevel(logging.DEBUG)
uvicorn_logger.setLevel(logging.DEBUG)


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server instance"""
    logger.info("Creating FastMCP server")
    server = FastMCP(
        "Conduit",
        host="localhost",
        port=8000,
        debug=True,
        log_level="DEBUG",
    )
    logger.info("FastMCP server instance created")
    logger.debug(f"Server attributes: {dir(server)}")
    logger.debug(f"Server configuration: {vars(server)}")

    # Register all tools with the server
    register_tools(server)

    return server


def register_tools(mcp_server: FastMCP) -> None:
    """Register all MCP tools with the server"""

    @mcp_server.tool(
        name="list_atlassian_sites",
        description="List all configured Jira and Confluence sites conduit is configured to use",
    )
    async def list_config() -> list[types.TextContent]:
        """List all configured Jira and Confluence sites"""
        try:
            logger.debug("Executing list_config tool")
            config = load_config()

            config_dict = {
                "jira": {
                    "default_site_alias": config.jira.default_site_alias,
                    "sites": {
                        alias: {
                            "url": site.url,
                            "email": site.email,
                            "api_token": "****",
                        }
                        for alias, site in config.jira.sites.items()
                    },
                },
                "confluence": {
                    "default_site_alias": config.confluence.default_site_alias,
                    "sites": {
                        alias: {
                            "url": site.url,
                            "email": site.email,
                            "api_token": "****",
                        }
                        for alias, site in config.confluence.sites.items()
                    },
                },
            }

            logger.debug(f"list_config result: {config_dict}")
            return [types.TextContent(type="text", text=str(config_dict))]
        except Exception as e:
            logger.error(f"Error in list_config: {e}", exc_info=True)
            raise

    @mcp_server.tool(
        name="get_confluence_page",
        description="Get Confluence page content by title within a space, returning the content in markdown format",
    )
    async def get_confluence_page(
        space_key: str, title: str, site_alias: Optional[Union[str, None]] = None
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

    @mcp_server.tool(
        name="search_jira_issues",
        description="Search for Jira issues using JQL (Jira Query Language) syntax",
    )
    async def search_jira_issues(
        query: str, site_alias: Optional[Union[str, None]] = None
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

    @mcp_server.tool(
        name="create_jira_issue",
        description="Create a new Jira issue with specified project, summary, description and type",
    )
    async def create_jira_issue(
        project: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        site_alias: Optional[Union[str, None]] = None,
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

    @mcp_server.tool(
        name="update_jira_issue",
        description="Update an existing Jira issue's summary and description fields",
    )
    async def update_jira_issue(
        key: str,
        summary: str,
        description: str,
        site_alias: Optional[Union[str, None]] = None,
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

            # Build update fields dictionary
            fields = {"summary": summary, "description": description}

            # Update the issue using the client
            client.update(key, **fields)

            # Get and return the updated issue
            updated_issue = client.get(key)
            logger.debug(f"update_jira_issue updated issue: {updated_issue}")
            return [types.TextContent(type="text", text=str(updated_issue))]
        except Exception as e:
            logger.error(f"Error in update_jira_issue: {e}", exc_info=True)
            raise

    @mcp_server.tool(
        name="update_jira_status",
        description="Update a Jira issue's status (move it to a different workflow state)",
    )
    async def update_jira_status(
        key: str,
        status: str,
        site_alias: Optional[Union[str, None]] = None,
    ) -> list[types.TextContent]:
        """Update a Jira issue's status"""
        try:
            logger.debug(
                f"Executing update_jira_status tool for issue '{key}' with new status '{status}' and site {site_alias}"
            )
            # Get the Jira client from the registry
            from conduit.platforms.registry import PlatformRegistry

            client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
            client.connect()

            # Transition the issue status using the client
            client.transition_status(key, status)

            # Get and return the updated issue
            updated_issue = client.get(key)
            logger.debug(f"update_jira_status updated issue: {updated_issue}")
            return [types.TextContent(type="text", text=str(updated_issue))]
        except Exception as e:
            logger.error(f"Error in update_jira_status: {e}", exc_info=True)
            raise

    @mcp_server.tool(
        name="get_jira_boards",
        description="Get all Jira boards, optionally filtered by project key",
    )
    async def get_jira_boards(
        project_key: Optional[Union[str, None]] = None,
        site_alias: Optional[Union[str, None]] = None,
    ) -> list[types.TextContent]:
        """Get all Jira boards, optionally filtered by project"""
        try:
            logger.debug(
                f"Executing get_jira_boards tool{f' for project {project_key}' if project_key else ''} with site {site_alias}"
            )
            # Get the Jira client from the registry
            from conduit.platforms.registry import PlatformRegistry

            client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
            client.connect()

            # Get boards using the client
            boards = client.get_boards(project_key)

            # Format the response as markdown
            markdown_response = "# Jira Boards\n\n"
            if project_key:
                markdown_response += f"Boards for project: {project_key}\n\n"

            if not boards:
                markdown_response += "No boards found.\n"
            else:
                markdown_response += f"Found {len(boards)} boards:\n\n"
                for board in boards:
                    markdown_response += (
                        f"- **{board.get('name', 'Unnamed Board')}**\n"
                        f"  - ID: {board.get('id')}\n"
                        f"  - Type: {board.get('type', 'Unknown')}\n"
                        f"  - Location: {board.get('location', {}).get('projectName', 'Unknown Project')}\n"
                    )

            logger.debug(f"get_jira_boards found {len(boards)} boards")
            return [types.TextContent(type="text", text=markdown_response)]
        except Exception as e:
            logger.error(f"Error in get_jira_boards: {e}", exc_info=True)
            raise

    @mcp_server.tool(
        name="get_jira_sprints",
        description="Get all sprints from a Jira board, optionally filtered by state (active, future, closed)",
    )
    async def get_jira_sprints(
        board_id: int,
        state: Optional[Union[str, None]] = None,
        site_alias: Optional[Union[str, None]] = None,
    ) -> list[types.TextContent]:
        """Get all sprints from a Jira board, optionally filtered by state"""
        try:
            logger.debug(
                f"Executing get_jira_sprints tool for board {board_id}{f' with state {state}' if state else ''} and site {site_alias}"
            )
            # Get the Jira client from the registry
            from conduit.platforms.registry import PlatformRegistry

            client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
            client.connect()

            # Get sprints using the client
            sprints = client.get_sprints(board_id, state)

            # Format the response as markdown
            markdown_response = "# Jira Sprints\n\n"
            markdown_response += f"Sprints for board ID: {board_id}\n"
            if state:
                markdown_response += f"Filtered by state: {state}\n"
            markdown_response += "\n"

            if not sprints:
                markdown_response += "No sprints found.\n"
            else:
                markdown_response += f"Found {len(sprints)} sprints:\n\n"
                for sprint in sprints:
                    markdown_response += (
                        f"- **{sprint.get('name', 'Unnamed Sprint')}**\n"
                        f"  - ID: {sprint.get('id')}\n"
                        f"  - State: {sprint.get('state', 'Unknown')}\n"
                        f"  - Start Date: {sprint.get('startDate', 'Not set')}\n"
                        f"  - End Date: {sprint.get('endDate', 'Not set')}\n"
                    )

            logger.debug(f"get_jira_sprints found {len(sprints)} sprints")
            return [types.TextContent(type="text", text=markdown_response)]
        except Exception as e:
            logger.error(f"Error in get_jira_sprints: {e}", exc_info=True)
            raise

    @mcp_server.tool(
        name="add_issues_to_jira_sprint",
        description="Add one or more Jira issues to a specific sprint by ID",
    )
    async def add_issues_to_jira_sprint(
        sprint_id: int,
        issue_keys: List[str],
        site_alias: Optional[Union[str, None]] = None,
    ) -> list[types.TextContent]:
        """Add one or more Jira issues to a sprint"""
        try:
            logger.debug(
                f"Executing add_issues_to_jira_sprint tool for sprint {sprint_id} with issues {issue_keys} and site {site_alias}"
            )
            # Get the Jira client from the registry
            from conduit.platforms.registry import PlatformRegistry

            client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
            client.connect()

            # Add issues to sprint
            client.add_issues_to_sprint(sprint_id, issue_keys)

            # Format the response as markdown
            markdown_response = "# Issues Added to Sprint\n\n"
            markdown_response += (
                f"Successfully added the following issues to sprint {sprint_id}:\n\n"
            )
            for key in issue_keys:
                issue = client.get(key)
                markdown_response += f"- **{key}**: {issue.get('fields', {}).get('summary', 'No summary')}\n"

            logger.debug(
                f"add_issues_to_jira_sprint added {len(issue_keys)} issues to sprint {sprint_id}"
            )
            return [types.TextContent(type="text", text=markdown_response)]
        except Exception as e:
            logger.error(f"Error in add_issues_to_jira_sprint: {e}", exc_info=True)
            raise

    @mcp_server.tool(
        name="get_jira_remote_links",
        description="Get all remote links (URLs, etc.) associated with a specific Jira issue",
    )
    async def get_jira_remote_links(
        key: str,
        site_alias: Optional[Union[str, None]] = None,
    ) -> list[types.TextContent]:
        """Get all remote links associated with a Jira issue"""
        try:
            logger.debug(
                f"Executing get_jira_remote_links tool for issue '{key}' with site {site_alias}"
            )
            # Get the Jira client from the registry
            from conduit.platforms.registry import PlatformRegistry

            client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
            client.connect()

            # Get remote links using the client
            links = client.get_remote_links(key)

            # Format the response as markdown
            markdown_response = f"# Remote Links for {key}\n\n"

            if not links:
                markdown_response += "No remote links found for this issue.\n"
            else:
                markdown_response += f"Found {len(links)} remote links:\n\n"
                for link in links:
                    relationship = link.get("relationship", "relates to")
                    object_data = link.get("object", {})
                    title = object_data.get("title", "No title")
                    url = object_data.get("url", "No URL")

                    markdown_response += (
                        f"- **{title}**\n"
                        f"  - Relationship: {relationship}\n"
                        f"  - URL: {url}\n\n"
                    )

            logger.debug(
                f"get_jira_remote_links found {len(links) if links else 0} remote links"
            )
            return [types.TextContent(type="text", text=markdown_response)]
        except Exception as e:
            logger.error(f"Error in get_jira_remote_links: {e}", exc_info=True)
            raise

    @mcp_server.tool(
        name="list_all_confluence_pages",
        description="List all pages in a Confluence space with pagination support, returning a formatted table of results",
    )
    async def list_all_confluence_pages(
        space_key: str,
        batch_size: int = 100,
        site_alias: Optional[Union[str, None]] = None,
    ) -> list[types.TextContent]:
        """List all pages in a Confluence space with pagination support"""
        try:
            logger.info(
                f"Listing all Confluence pages in space {space_key} with batch size {batch_size}"
            )

            # Get the Confluence client from the registry
            from conduit.platforms.registry import PlatformRegistry

            client = PlatformRegistry.get_platform("confluence", site_alias=site_alias)
            client.connect()

            # Get pages using the client's get_pages_by_space method
            pages = client.get_pages_by_space(space_key, limit=batch_size)

            # Format the response
            result = f"# Pages in {space_key} space\n\n"
            if pages:
                result += "| Title | ID | URL |\n"
                result += "|-------|----|---------|\n"
                for page in pages:
                    title = page.get("title", "Untitled")
                    page_id = page.get("id", "Unknown")
                    url = page.get("_links", {}).get("webui", "")
                    result += f"| {title} | {page_id} | {url} |\n"
            else:
                result += "No pages found in this space."

            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Error listing Confluence pages: {e}", exc_info=True)
            return [
                types.TextContent(
                    type="text", text=f"# Error listing Confluence pages\n\n{str(e)}"
                )
            ]

    @mcp_server.tool(
        name="create_confluence_page_from_markdown",
        description="Create a new Confluence page from markdown content, automatically converting it to Confluence storage format",
    )
    async def create_confluence_page(
        space: str,
        title: str,
        content: str,
        parent_id: Optional[Union[str, int]] = None,
        site_alias: Optional[Union[str, None]] = None,
    ) -> list[types.TextContent]:
        """Create a new Confluence page with markdown content"""
        try:
            logger.info(f"Creating Confluence page in space {space} with title {title}")

            # Use the existing service to create the page
            page = await ConfluenceService.create_page_from_markdown(
                space_key=space,
                title=title,
                content=content,
                parent_id=parent_id,
                site_alias=site_alias,
            )

            # Format the response
            result = f"# Page created successfully\n\n"
            result += f"- **Title**: {title}\n"
            result += f"- **Space**: {space}\n"
            result += f"- **ID**: {page['id']}\n"
            result += f"- **URL**: {page['url']}\n"

            if parent_id:
                result += f"- **Parent ID**: {parent_id}\n"

            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Error creating Confluence page: {e}", exc_info=True)
            return [
                types.TextContent(
                    type="text", text=f"# Error creating Confluence page\n\n{str(e)}"
                )
            ]


# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()


@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    """Entry point for the MCP server"""
    try:
        if transport == "stdio":
            asyncio.run(server.run_stdio_async())
        else:
            asyncio.run(server.run_sse_async())
        return 0
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
