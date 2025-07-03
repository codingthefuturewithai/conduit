"""MCP server implementation for Conduit"""

import datetime
import logging
import sys
from typing import Any, Dict, List

import click
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from conduit.core.config import load_config
from conduit.core.services import ConfluenceService
from conduit.platforms.registry import PlatformRegistry


class AttachmentSpec(BaseModel):
    """Specification for a file attachment"""
    local_path: str
    name_on_confluence: str

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
        space_key: str, title: str, site_alias: str = None
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
        query: str, site_alias: str = None
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
        site_alias: str = None,
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
        site_alias: str = None,
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
        site_alias: str = None,
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
        project_key: str = None,
        site_alias: str = None,
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
        state: str = None,
        site_alias: str = None,
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
        site_alias: str = None,
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
        name="create_jira_sprint",
        description="Create a new sprint on a Jira board with a mandatory goal and optional start/end dates",
    )
    async def create_jira_sprint(
        name: str,
        board_id: int,
        goal: str,
        start_date: str = None,
        end_date: str = None,
        site_alias: str = None,
    ) -> list[types.TextContent]:
        """Create a new sprint on a Jira board with a mandatory goal"""
        try:
            # Ensure board_id is an integer
            board_id = int(board_id)

            logger.debug(
                f"Executing create_jira_sprint tool for board {board_id} with name '{name}', goal '{goal}' and site {site_alias}"
            )
            # Get the Jira client from the registry
            from conduit.platforms.registry import PlatformRegistry

            client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
            client.connect()

            # Create the sprint using the client - note the parameter order matches the client's create_sprint method
            sprint = client.create_sprint(name, board_id, start_date, end_date, goal)

            # Format the response as markdown
            markdown_response = "# Sprint Created Successfully\n\n"
            markdown_response += f"- **Name**: {sprint.get('name')}\n"
            markdown_response += f"- **ID**: {sprint.get('id')}\n"
            markdown_response += f"- **State**: {sprint.get('state')}\n"
            markdown_response += f"- **Board ID**: {board_id}\n"
            markdown_response += f"- **Goal**: {sprint.get('goal')}\n"

            if start_date:
                markdown_response += f"- **Start Date**: {sprint.get('startDate')}\n"
            if end_date:
                markdown_response += f"- **End Date**: {sprint.get('endDate')}\n"

            logger.debug(
                f"create_jira_sprint created sprint with ID {sprint.get('id')}"
            )
            return [types.TextContent(type="text", text=markdown_response)]
        except Exception as e:
            # Log the error with more details
            logger.error(f"Error in create_jira_sprint: {e}", exc_info=True)
            logger.error(
                f"Parameters received - name: {name}, board_id: {board_id}, goal: {goal}, start_date: {start_date}, end_date: {end_date}, site_alias: {site_alias}"
            )

            # If it's a validation error, provide more helpful information
            if "validation error" in str(e).lower():
                return [
                    types.TextContent(
                        type="text",
                        text=f"# Validation Error\n\nThere was an error validating the input parameters: {e}\n\nPlease ensure all required fields are filled out correctly. The board_id must be a valid integer.",
                    )
                ]

            raise

    @mcp_server.tool(
        name="get_jira_remote_links",
        description="Get all remote links (URLs, etc.) associated with a specific Jira issue",
    )
    async def get_jira_remote_links(
        key: str,
        site_alias: str = None,
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
        name="create_confluence_page_from_markdown",
        description="Create a new Confluence page from markdown content, automatically converting it to Confluence storage format. "
        "Can attach and embed images - use standard markdown syntax: ![alt text](filename.png). "
        "Images referenced in markdown that match attachment filenames will be automatically embedded.",
    )
    async def create_confluence_page(
        space: str,
        title: str,
        content: str,
        parent_id: str = None,
        site_alias: str = None,
        attachments: List[AttachmentSpec] = None,
    ) -> list[types.TextContent]:
        """Create a new Confluence page with markdown content and optional attachments.

        Args:
            space: The key of the Confluence space
            title: The title of the page to create
            content: Markdown content with standard markdown image syntax
            parent_id: Optional ID of the parent page
            site_alias: Optional site alias for multi-site configurations
            attachments: Optional list of attachments, each with:
                - local_path: Path to the file on local filesystem
                - name_on_confluence: Name for the attachment on Confluence

        To embed attached images, use standard markdown syntax:
        ![Image description](filename.png)
        
        The filename must match the name_on_confluence of an attachment.
        """
        try:
            logger.info(f"Creating Confluence page in space {space} with title {title}")
            logger.warning(f"DEBUG CREATE: Received attachments parameter: {attachments}, type: {type(attachments)}")
            if attachments:
                logger.info(f"Will attach {len(attachments)} file(s)")

            # Use the existing service to create the page
            # Convert AttachmentSpec objects to dicts for the service
            attachment_dicts = None
            if attachments:
                # Handle both dict and AttachmentSpec objects
                attachment_dicts = []
                for att in attachments:
                    if isinstance(att, dict):
                        attachment_dicts.append(att)
                    else:
                        attachment_dicts.append(att.model_dump())
            
            page = await ConfluenceService.create_page_from_markdown(
                space_key=space,
                title=title,
                content=content,
                parent_id=parent_id,
                site_alias=site_alias,
                attachments=attachment_dicts,
            )

            # Format the response
            result = "# Page created successfully\n\n"
            result += f"- **Title**: {title}\n"
            result += f"- **Space**: {space}\n"
            result += f"- **ID**: {page['id']}\n"
            result += f"- **Version**: {page['version']}\n"  # Access version directly from the service response
            result += f"- **URL**: {page['url']}\n"

            if parent_id:
                result += f"- **Parent ID**: {parent_id}\n"

            if attachments:
                result += "\n## Attachments\n"
                result += f"Successfully attached {len(attachments)} file(s):\n"
                for att in attachments:
                    if isinstance(att, dict):
                        result += f"- {att['name_on_confluence']}\n"
                    else:
                        result += f"- {att.name_on_confluence}\n"

            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logger.error(f"Error creating Confluence page: {e}", exc_info=True)
            return [
                types.TextContent(
                    type="text", text=f"# Error creating Confluence page\n\n{str(e)}"
                )
            ]

    @mcp_server.tool(
        name="get_project_overview",
        description="Get a unified view of project information from both Jira and Confluence",
    )
    async def get_project_overview(
        project_key: str,
        space_key: str,
        site_alias: str = None,
    ) -> list[types.TextContent]:
        """Get a unified view of project information from both Jira and Confluence"""
        try:
            logger.info(
                f"Executing get_project_overview for project {project_key} and space {space_key} with site {site_alias}"
            )

            # Get the Jira and Confluence clients from the registry
            from conduit.platforms.registry import PlatformRegistry

            jira_client = PlatformRegistry.get_platform("jira", site_alias=site_alias)
            jira_client.connect()

            confluence_client = PlatformRegistry.get_platform(
                "confluence", site_alias=site_alias
            )
            confluence_client.connect()

            # Initialize the response structure
            overview = {
                "project_key": project_key,
                "space_key": space_key,
                "jira": {
                    "boards": [],
                    "active_sprints": [],
                    "issue_counts": {
                        "to_do": 0,
                        "in_progress": 0,
                        "done": 0,
                        "total": 0,
                    },
                },
                "confluence": {"pages": []},
            }

            # Get Jira boards for the project
            boards = jira_client.get_boards(project_key)
            overview["jira"]["boards"] = boards

            # Get active sprints for each board
            active_sprints = []
            for board in boards:
                board_id = board.get("id")
                if board_id:
                    sprints = jira_client.get_sprints(board_id, "active")
                    active_sprints.extend(sprints)
            overview["jira"]["active_sprints"] = active_sprints

            # Get issue counts by status
            # To Do issues
            to_do_query = f'project = "{project_key}" AND status = "To Do"'
            to_do_issues = jira_client.search(to_do_query)
            overview["jira"]["issue_counts"]["to_do"] = len(to_do_issues)

            # In Progress issues
            in_progress_query = f'project = "{project_key}" AND status = "In Progress"'
            in_progress_issues = jira_client.search(in_progress_query)
            overview["jira"]["issue_counts"]["in_progress"] = len(in_progress_issues)

            # Done issues
            done_query = f'project = "{project_key}" AND status = "Done"'
            done_issues = jira_client.search(done_query)
            overview["jira"]["issue_counts"]["done"] = len(done_issues)

            # Total issues
            total_query = f'project = "{project_key}"'
            total_issues = jira_client.search(total_query)
            overview["jira"]["issue_counts"]["total"] = len(total_issues)

            # Get Confluence pages
            pages = confluence_client.get_pages_by_space(space_key)
            overview["confluence"]["pages"] = pages

            # Format the response as markdown
            markdown_response = f"# Project Overview: {project_key} / {space_key}\n\n"

            # Jira Boards section
            markdown_response += "## Jira Boards\n\n"
            if not boards:
                markdown_response += "No boards found for this project.\n\n"
            else:
                markdown_response += f"Found {len(boards)} boards:\n\n"
                for board in boards:
                    markdown_response += (
                        f"- **{board.get('name', 'Unnamed Board')}**\n"
                        f"  - ID: {board.get('id')}\n"
                        f"  - Type: {board.get('type', 'Unknown')}\n"
                    )
                markdown_response += "\n"

            # Active Sprints section
            markdown_response += "## Active Sprints\n\n"
            if not active_sprints:
                markdown_response += "No active sprints found.\n\n"
            else:
                markdown_response += f"Found {len(active_sprints)} active sprints:\n\n"
                for sprint in active_sprints:
                    markdown_response += (
                        f"- **{sprint.get('name', 'Unnamed Sprint')}**\n"
                        f"  - ID: {sprint.get('id')}\n"
                        f"  - Start Date: {sprint.get('startDate', 'Not set')}\n"
                        f"  - End Date: {sprint.get('endDate', 'Not set')}\n"
                    )
                markdown_response += "\n"

            # Issue Counts section
            markdown_response += "## Issue Counts\n\n"
            markdown_response += "| Status | Count |\n"
            markdown_response += "|--------|-------|\n"
            markdown_response += (
                f"| To Do | {overview['jira']['issue_counts']['to_do']} |\n"
            )
            markdown_response += (
                f"| In Progress | {overview['jira']['issue_counts']['in_progress']} |\n"
            )
            markdown_response += (
                f"| Done | {overview['jira']['issue_counts']['done']} |\n"
            )
            markdown_response += (
                f"| **Total** | **{overview['jira']['issue_counts']['total']}** |\n\n"
            )

            # Confluence Pages section
            markdown_response += "## Confluence Pages\n\n"
            if not pages:
                markdown_response += "No pages found in this space.\n"
            else:
                markdown_response += f"Found {len(pages)} pages:\n\n"
                markdown_response += "| Title | ID | Last Updated |\n"
                markdown_response += "|-------|----|--------------|\n"
                for page in pages[:10]:  # Limit to 10 pages for readability
                    title = page.get("title", "Untitled")
                    page_id = page.get("id", "Unknown")
                    last_updated = page.get("version", {}).get("when", "Unknown")
                    markdown_response += f"| {title} | {page_id} | {last_updated} |\n"

                if len(pages) > 10:
                    markdown_response += f"\n*...and {len(pages) - 10} more pages*\n"

            # Add a simple cache hint
            markdown_response += (
                "\n\n*Data retrieved at: "
                + f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            )

            logger.debug(
                f"get_project_overview completed for {project_key}/{space_key}"
            )
            return [types.TextContent(type="text", text=markdown_response)]
        except Exception as e:
            logger.error(f"Error in get_project_overview: {e}", exc_info=True)
            return [
                types.TextContent(
                    type="text", text=f"# Error retrieving project overview\n\n{str(e)}"
                )
            ]

    @mcp_server.tool(
        name="update_confluence_page_from_markdown",
        description="Update an existing Confluence page with markdown content, automatically converting it to Confluence storage format. "
        "Supports version conflict detection and marking updates as minor edits. "
        "Can attach and embed images - use standard markdown syntax: ![alt text](filename.png). "
        "Images referenced in markdown that match attachment filenames will be automatically embedded.",
    )
    async def update_confluence_page(
        space_key: str,
        title: str,
        content: str,
        expected_version: int,
        site_alias: str = None,
        minor_edit: bool = False,  # Set to True for small changes like typo fixes or formatting adjustments
        attachments: List[AttachmentSpec] = None,
    ) -> list[types.TextContent]:
        """Update a Confluence page with version conflict detection and optional attachments.

        Args:
            space_key: The key of the space containing the page
            title: The title of the page to update
            content: New markdown content with standard markdown image syntax
            expected_version: The version number we expect the page to be at
            site_alias: Optional site alias for multi-site configurations
            minor_edit: Set to True for small changes (typos, formatting) to avoid notification spam.
                       Set to False for substantial content changes that watchers should know about.
            attachments: Optional list of attachments, each with:
                - local_path: Path to the file on local filesystem
                - name_on_confluence: Name for the attachment on Confluence

        To embed attached images, use standard markdown syntax:
        ![Image description](filename.png)
        
        The filename must match the name_on_confluence of an attachment.
        """
        try:
            logger.debug(
                f"Executing update_confluence_page for '{title}' in space {space_key} with expected version {expected_version}"
            )
            logger.warning(f"DEBUG: Received attachments parameter: {attachments}, type: {type(attachments)}")
            if attachments:
                logger.info(f"Will attach {len(attachments)} file(s)")

            try:
                # Convert AttachmentSpec objects to dicts for the service
                attachment_dicts = None
                if attachments:
                    # Handle both dict and AttachmentSpec objects
                    attachment_dicts = []
                    for att in attachments:
                        if isinstance(att, dict):
                            attachment_dicts.append(att)
                        else:
                            attachment_dicts.append(att.model_dump())
                
                # Use the service to update the page
                page = await ConfluenceService.update_page_from_markdown(
                    space_key=space_key,
                    title=title,
                    content=content,
                    expected_version=expected_version,
                    site_alias=site_alias,
                    minor_edit=minor_edit,
                    attachments=attachment_dicts,
                )

                # Return success message with new version info
                result = f"""# Page Updated Successfully

- Title: {title}
- Space: {space_key}
- New Version: {page.get('response', {}).get('version', {}).get('number')}
- Last Updated: {page.get('response', {}).get('version', {}).get('when')}
- URL: {page.get('url')}"""

                if attachments:
                    result += f"\n\n## Attachments\nSuccessfully attached {len(attachments)} file(s):\n"
                    for att in attachments:
                        if isinstance(att, dict):
                            result += f"- {att['name_on_confluence']}\n"
                        else:
                            result += f"- {att.name_on_confluence}\n"

                result += "\n\nThe page has been updated successfully."

                return [types.TextContent(type="text", text=result)]

            except ValueError as e:
                if "Version mismatch" in str(e):
                    # Get current page info for helpful error message
                    client = PlatformRegistry.get_platform(
                        "confluence", site_alias=site_alias
                    )
                    client.connect()
                    current_page = client.get_page_by_title(space_key, title)

                    return [
                        types.TextContent(
                            type="text",
                            text=f"""# Version Conflict Detected

The page has been modified since you last retrieved it.
- Your version: {expected_version}
- Current version: {current_page.get('version', {}).get('number')}
- Last modified: {current_page.get('version', {}).get('when')}

Please retrieve the latest version and merge your changes.

To help with merging, here are the options:
1. Get the latest version using `get_confluence_page` to see recent changes
2. Modify your changes to incorporate any updates
3. Try the update again with the new version number

Would you like me to fetch the latest version for you?""",
                        )
                    ]
                else:
                    return [types.TextContent(type="text", text=f"# Error\n{str(e)}")]

        except Exception as e:
            logger.error(f"Error in update_confluence_page: {e}", exc_info=True)
            return [
                types.TextContent(
                    type="text", text=f"# Error updating Confluence page\n\n{str(e)}"
                )
            ]

    @mcp_server.tool(
        name="retrieve_confluence_hierarchy",
        description="Retrieve Confluence pages in a hierarchical tree structure. "
        "Can start from space root or a specific parent page, with configurable depth and batch limits.",
    )
    async def retrieve_confluence_hierarchy(
        space_key: str,
        parent_page_id: str = None,
        batch_size: int = 100,
        max_depth: int = None,
        site_alias: str = None,
    ) -> list[types.TextContent]:
        """Retrieve Confluence pages in a hierarchical tree structure.

        Args:
            space_key: The Confluence space key (required)
            parent_page_id: Optional page ID to start from; if not provided, starts from space root
            batch_size: Maximum number of pages to retrieve (default: 100)
            max_depth: Optional maximum depth to traverse
            site_alias: Optional site alias for multi-site configurations
        """
        try:
            logger.debug(
                f"Executing retrieve_confluence_hierarchy for space {space_key}, "
                f"parent: {parent_page_id or 'root'}, batch_size: {batch_size}, "
                f"max_depth: {max_depth}, site: {site_alias}"
            )

            # Get the Confluence client from the registry
            client = PlatformRegistry.get_platform("confluence", site_alias=site_alias)
            client.connect()

            # Get the hierarchical structure
            hierarchy = client.get_page_hierarchy(
                space_key=space_key,
                parent_page_id=parent_page_id,
                batch_size=batch_size,
                max_depth=max_depth,
            )

            # Format the response as markdown with the tree structure
            markdown_response = "# Confluence Page Hierarchy\n\n"
            markdown_response += f"**Space**: {space_key}\n"
            if parent_page_id:
                markdown_response += f"**Starting from page ID**: {parent_page_id}\n"
            else:
                markdown_response += "**Starting from**: Space root\n"
            markdown_response += (
                f"**Total pages retrieved**: {hierarchy['total_pages']}\n"
            )
            markdown_response += f"**Batch size limit**: {batch_size}\n"
            if max_depth:
                markdown_response += f"**Max depth**: {max_depth}\n"
            markdown_response += "\n## Page Tree\n\n"

            def format_tree_node(node: Dict[str, Any], indent: int = 0) -> str:
                """Format a node and its children as a tree structure."""
                result = "  " * indent + f"- **{node['title']}**\n"
                result += "  " * indent + f"  - ID: {node['id']}\n"
                result += "  " * indent + f"  - Version: {node['version']}\n"
                result += "  " * indent + f"  - Last Updated: {node['lastUpdated']}\n"
                if node["url"]:
                    result += "  " * indent + f"  - URL: {node['url']}\n"

                # Format children
                for child in node["children"]:
                    result += format_tree_node(child, indent + 1)

                return result

            # Format the hierarchy
            if not hierarchy["hierarchy"]:
                markdown_response += "*No pages found*\n"
            else:
                for root_node in hierarchy["hierarchy"]:
                    markdown_response += format_tree_node(root_node)

            # Add note if batch size was reached
            if hierarchy["total_pages"] >= batch_size:
                markdown_response += (
                    f"\n**Note**: Batch size limit of {batch_size} pages was reached. "
                    "There may be additional pages not shown.\n"
                )

            logger.debug(
                f"retrieve_confluence_hierarchy completed, retrieved {hierarchy['total_pages']} pages"
            )
            return [types.TextContent(type="text", text=markdown_response)]

        except Exception as e:
            logger.error(f"Error in retrieve_confluence_hierarchy: {e}", exc_info=True)
            return [
                types.TextContent(
                    type="text",
                    text=f"# Error retrieving Confluence hierarchy\n\n{str(e)}",
                )
            ]


# Create a server instance that can be imported by the MCP CLI
server = create_mcp_server()


@click.command()
@click.option(
    "--version", is_flag=True, help="Show the Conduit MCP server version and exit."
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
def main(version: bool, transport: str):
    """Entry point for the MCP server"""
    if version:
        import importlib.metadata

        try:
            version_str = importlib.metadata.version("conduit-connect")
            click.echo(f"Conduit MCP server version {version_str}")
        except importlib.metadata.PackageNotFoundError:
            click.echo("Conduit MCP server version unknown (package not installed)")
        sys.exit(0)

    # Imports below are intentionally placed here to avoid side effects
    # when --version is passed (no server or logging should be initialized).
    import asyncio

    from conduit.core.logger import logger
    from conduit.mcp import server

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
