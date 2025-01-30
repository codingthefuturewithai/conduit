import click
from conduit.platforms.registry import PlatformRegistry
from conduit.core.exceptions import PlatformError
from conduit.cli.commands.jira import jira


@click.group()
def cli():
    """Conduit - Enterprise Knowledge Integration Service."""
    pass


# Register commands
cli.add_command(jira)


@cli.command()
@click.argument("platform_name")
def connect(platform_name):
    """Connect to a platform."""
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        click.echo(f"Connected to {platform_name}")
    except PlatformError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("platform_name")
@click.argument("issue_key")
def get_issue(platform_name, issue_key):
    """Get an issue by key."""
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
    """Search for issues."""
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
@click.option("--summary", required=True, help="Summary of the issue")
@click.option("--description", default="", help="Description of the issue")
def create_issue(platform_name, project_key, summary, description):
    """Create a new issue in the specified project."""
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        issue = platform.create(
            project={"key": project_key},
            summary=summary,
            description=description,
            issuetype={"name": "Task"},
        )
        click.echo(f"Issue created: {issue}")
    except PlatformError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("platform_name")
@click.argument("issue_key")
@click.option("--summary", help="New summary of the issue")
def update_issue(platform_name, issue_key, summary):
    """Update an existing issue."""
    try:
        platform = PlatformRegistry.get_platform(platform_name)
        platform.connect()
        platform.update(issue_key, summary=summary)
        click.echo(f"Issue {issue_key} updated")
    except PlatformError as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    cli()
