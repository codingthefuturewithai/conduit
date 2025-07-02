from pathlib import Path

import click

from conduit.core.config import load_config
from conduit.core.content import ContentManager
from conduit.platforms.registry import PlatformRegistry


@click.group()
def jira():
    """Jira issue tracking commands.

    Commands for managing Jira issues:
      • Create and update issues
      • Add comments to issues
      • Transition issue status
      • Search using JQL queries

    Requires Jira credentials in ~/.config/conduit/config.yaml
    """
    pass


@jira.group()
def issue():
    """Commands for managing individual Jira issues.

    Supports operations like:
      • Get issue details
      • Create/update issues
      • Add comments
      • Change status
    """
    pass


@issue.command()
@click.argument("key")
@click.option("--site", help="Site alias to use for this operation")
def get(key, site):
    """Get complete details of a Jira issue.

    Example: conduit jira issue get PROJ-123 [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        result = platform.get(key)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("query")
@click.option("--site", help="Site alias to use for this operation")
def search(query, site):
    """Search Jira issues using JQL syntax.

    Supports full JQL (Jira Query Language) for advanced filtering.
    Example: conduit jira issue search "project = PROJ AND status = 'In Progress'" [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        results = platform.search(query)
        click.echo(results)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("project")
@click.option("--summary", required=True, help="Issue title/summary")
@click.option(
    "--content-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to file containing the formatted content for description",
)
@click.option("--type", default="Task", help="Issue type (Task, Bug, Story, etc.)")
@click.option("--site", help="Site alias to use for this operation")
def create(project, summary, content_file, type, site):
    """Create a new Jira issue.

    Creates an issue with specified fields in the given project.
    The description must be provided via a content file.

    Example:
        $ path=$(conduit get-content-path)
        $ echo "# Description\\n\\nDetailed description" > "$path"
        $ conduit jira issue create PROJ --summary "New Feature" --content-file "$path" --type Story [--site site1]
    """
    content_file_path = Path(content_file)
    config = load_config()
    content_manager = ContentManager(config.get_content_dir())

    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()

        description = content_manager.read_content(content_file_path)
        result = platform.create(
            project={"key": project},
            summary=summary,
            description=description,
            issuetype={"name": type},
        )

        # Only cleanup the file if it's in our content directory
        if str(content_file_path.absolute()).startswith(
            str(config.get_content_dir().absolute())
        ):
            content_manager.cleanup_content_file(content_file_path)

        click.echo(result)
    except Exception as e:
        # Only move to failed if it's in our content directory
        if str(content_file_path.absolute()).startswith(
            str(config.get_content_dir().absolute())
        ):
            try:
                failed_path = content_manager.mark_content_as_failed(content_file_path)
                click.echo(f"Content file moved to: {failed_path}")
            except Exception as move_error:
                click.echo(
                    f"Warning: Failed to move content file: {move_error}", err=True
                )

        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("key")
@click.option("--summary", help="New issue title/summary")
@click.option("--description", help="New issue description")
@click.option(
    "--content-file",
    type=click.Path(exists=True),
    help="Path to file containing the formatted content for description",
)
@click.option("--site", help="Site alias to use for this operation")
def update(key, summary, description, content_file, site):
    """Update an existing Jira issue's fields.

    Modify the summary and/or description of the specified issue.
    The description can be provided directly or via a content file.

    Example:
      Direct update:
        $ conduit jira issue update PROJ-123 --summary "Updated Feature" [--site site1]

      Update with content file:
        $ path=$(conduit get-content-path)
        $ echo "# Updated Description\\n\\nNew content" > "$path"
        $ conduit jira issue update PROJ-123 --content-file "$path" [--site site1]
    """
    content_file_path = Path(content_file) if content_file else None
    config = load_config()
    content_manager = ContentManager(config.get_content_dir())

    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        fields = {}

        if summary:
            fields["summary"] = summary

        if content_file_path:
            fields["description"] = content_manager.read_content(content_file_path)
        elif description:
            fields["description"] = description

        platform.update(key, **fields)

        # Only cleanup the file if it's in our content directory
        if content_file_path and str(content_file_path.absolute()).startswith(
            str(config.get_content_dir().absolute())
        ):
            content_manager.cleanup_content_file(content_file_path)

        click.echo(f"Successfully updated issue {key}")
    except Exception as e:
        # Only move to failed if it's in our content directory
        if content_file_path and str(content_file_path.absolute()).startswith(
            str(config.get_content_dir().absolute())
        ):
            try:
                failed_path = content_manager.mark_content_as_failed(content_file_path)
                click.echo(f"Content file moved to: {failed_path}")
            except Exception as move_error:
                click.echo(
                    f"Warning: Failed to move content file: {move_error}", err=True
                )

        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("key")
@click.option(
    "--content-file",
    type=click.Path(exists=True),
    required=True,
    help="Path to file containing the formatted comment content",
)
@click.option("--site", help="Site alias to use for this operation")
def comment(key, content_file, site):
    """Add a comment to a Jira issue.

    Posts a new comment on the specified issue. The comment content must be provided
    in a file that can contain markdown formatting.

    Example:
        $ path=$(conduit get-content-path)
        $ echo "# Comment\\n\\n- Progress update\\n- Next steps" > "$path"
        $ conduit jira issue comment PROJ-123 --content-file "$path" [--site site1]
    """
    content_file_path = Path(content_file)
    config = load_config()
    content_manager = ContentManager(config.get_content_dir())

    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()

        comment_text = content_manager.read_content(content_file_path)
        result = platform.add_comment(key, comment_text)

        # Only cleanup the file if it's in our content directory
        if str(content_file_path.absolute()).startswith(
            str(config.get_content_dir().absolute())
        ):
            content_manager.cleanup_content_file(content_file_path)

        click.echo(f"Successfully added comment to issue {key}")
        click.echo(result)
    except Exception as e:
        # Only move to failed if it's in our content directory
        if str(content_file_path.absolute()).startswith(
            str(config.get_content_dir().absolute())
        ):
            try:
                failed_path = content_manager.mark_content_as_failed(content_file_path)
                click.echo(f"Content file moved to: {failed_path}")
            except Exception as move_error:
                click.echo(
                    f"Warning: Failed to move content file: {move_error}", err=True
                )

        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("key")
@click.argument("status")
@click.option("--site", help="Site alias to use for this operation")
def status(key, status, site):
    """Update a Jira issue's status.

    Transitions the issue to a new workflow status.
    Example: conduit jira issue status PROJ-123 "In Progress" [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        platform.transition_status(key, status)
        click.echo(f"Successfully transitioned issue {key} to '{status}'")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("key")
@click.option("--site", help="Site alias to use for this operation")
def remote_links(key, site):
    """Get all remote links associated with a Jira issue.

    Lists all external links (URLs) that have been added to the issue.
    Example: conduit jira issue remote-links PROJ-123 [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        links = platform.get_remote_links(key)
        if not links:
            click.echo("No remote links found for this issue.")
            return
        for link in links:
            relationship = link.get("relationship", "relates to")
            object_data = link.get("object", {})
            title = object_data.get("title", "No title")
            url = object_data.get("url", "No URL")
            click.echo(f"\n{title}")
            click.echo(f"Relationship: {relationship}")
            click.echo(f"URL: {url}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@jira.command()
@click.option("--project", required=True, help="Project key to get boards for")
@click.option("--site", help="Site alias to use for this operation")
def get_boards(project, site):
    """Get all boards for a project.

    Lists all boards associated with the specified project.
    Example: conduit jira get-boards --project PROJ [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        boards = platform.get_boards(project)
        if not boards:
            click.echo(f"No boards found for project {project}")
            return
        click.echo(f"\nBoards for project {project}:")
        for board in boards:
            click.echo(
                f"- {board.get('name', 'Unnamed Board')} (ID: {board.get('id')})"
            )
            click.echo(f"  Type: {board.get('type', 'Unknown')}")
            click.echo(
                f"  Location: {board.get('location', {}).get('projectName', 'Unknown Project')}\n"
            )
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@jira.command()
@click.argument("board_id")
@click.option(
    "--state",
    type=click.Choice(["active", "future", "closed"]),
    help="Filter sprints by state",
)
@click.option("--site", help="Site alias to use for this operation")
def get_sprints(board_id, state, site):
    """Get all sprints from a board.

    Lists all sprints associated with the specified board, optionally filtered by state.
    Example: conduit jira get-sprints BOARD-123 --state active [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        sprints = platform.get_sprints(board_id, state)
        if not sprints:
            click.echo(f"No sprints found for board {board_id}")
            return
        click.echo(f"\nSprints for board {board_id}:")
        for sprint in sprints:
            click.echo(
                f"- {sprint.get('name', 'Unnamed Sprint')} (ID: {sprint.get('id')})"
            )
            click.echo(f"  State: {sprint.get('state', 'Unknown')}")
            click.echo(f"  Start Date: {sprint.get('startDate', 'Not set')}")
            click.echo(f"  End Date: {sprint.get('endDate', 'Not set')}\n")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@jira.command()
@click.argument("sprint_id")
@click.option(
    "--issues", required=True, multiple=True, help="Issue keys to add to the sprint"
)
@click.option("--site", help="Site alias to use for this operation")
def add_to_sprint(sprint_id, issues, site):
    """Add issues to a sprint.

    Adds one or more issues to the specified sprint.
    Example: conduit jira add-to-sprint SPRINT-456 --issues PROJ-123 PROJ-124 [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
        platform.connect()
        platform.add_issues_to_sprint(sprint_id, list(issues))
        click.echo(
            f"Successfully added issues {', '.join(issues)} to sprint {sprint_id}"
        )
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)
