import click

from conduit.platforms.registry import PlatformRegistry
from conduit.core.exceptions import PlatformError
from conduit.cli.commands.jira import jira
from conduit.cli.commands.confluence import confluence


@click.group()
def cli():
    """Conduit: Enterprise Knowledge Integration Service

    A unified CLI for Jira and Confluence integration.

    Core Features:
      • Jira issue management
      • Confluence documentation access
      • Seamless platform integration
      • AI-optimized content formatting

    Configuration: ~/.config/conduit/config.yaml

    Examples:
      $ conduit jira issue create --project PROJ --summary "New Feature"
      $ conduit confluence pages content SPACE --format clean
      $ conduit jira issue comment PROJ-123 "Work in progress"
    """
    pass


# Register commands
cli.add_command(jira)
cli.add_command(confluence)


@cli.command()
@click.argument("platform_name")
def connect(platform_name):
    """Test connection to a platform (jira/confluence).

    Validates your credentials and connection settings for the specified platform.
    Example: conduit connect jira
    """
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        click.echo(f"Successfully connected to {platform_name}")
    except PlatformError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("platform_name")
@click.argument("issue_key")
def get_issue(platform_name, issue_key):
    """Retrieve full details of a Jira issue.

    Fetches all fields, comments, and metadata for the specified issue.
    Example: conduit get-issue jira PROJ-123
    """
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        issue = platform.get(issue_key)
        click.echo(issue)
    except PlatformError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("platform_name")
@click.argument("query")
def search_issues(platform_name, query):
    """Search for Jira issues using JQL.

    Supports full JQL (Jira Query Language) syntax for advanced searching.
    Example: conduit search-issues jira "project = PROJ AND status = 'In Progress'"
    """
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        issues = platform.search(query)
        click.echo(issues)
    except PlatformError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("platform_name")
@click.argument("project_key")
@click.option("--summary", required=True, help="Title/summary of the issue")
@click.option("--description", default="", help="Detailed description of the issue")
def create_issue(platform_name, project_key, summary, description):
    """Create a new Jira issue in the specified project.

    Creates a Task-type issue with the given summary and description.
    Example: conduit create-issue jira PROJ --summary "New feature" --description "Details..."
    """
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        issue = platform.create(
            project={"key": project_key},
            summary=summary,
            description=description,
            issuetype={"name": "Task"},
        )
        click.echo(issue)
    except PlatformError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("platform_name")
@click.argument("issue_key")
@click.option("--summary", help="New summary/title for the issue")
@click.option("--description", help="New description for the issue")
def update_issue(platform_name, issue_key, summary, description):
    """Update an existing Jira issue's fields.

    Modify the summary and/or description of an existing issue.
    Example: conduit update-issue jira PROJ-123 --summary "Updated title"
    """
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = description
        platform.update(issue_key, **fields)
        click.echo(f"Successfully updated issue {issue_key}")
    except PlatformError as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    cli()
