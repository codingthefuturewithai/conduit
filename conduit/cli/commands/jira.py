import click
from conduit.platforms.registry import PlatformRegistry
from conduit.core.exceptions import PlatformError


@click.group()
def jira():
    """Jira commands."""
    pass


@jira.group()
def issue():
    """Issue management commands."""
    pass


@issue.command()
@click.argument("key")
def get(key):
    """Get an issue by key."""
    try:
        platform = PlatformRegistry.get_platform("jira")
        platform.connect()
        result = platform.get(key)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("query")
def search(query):
    """Search issues using JQL."""
    try:
        platform = PlatformRegistry.get_platform("jira")
        platform.connect()
        results = platform.search(query)
        click.echo(results)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.option("--project", required=True, help="Project key")
@click.option("--summary", required=True, help="Issue summary")
@click.option("--description", default="", help="Issue description")
@click.option("--type", default="Task", help="Issue type")
def create(project, summary, description, type):
    """Create a new issue."""
    try:
        platform = PlatformRegistry.get_platform("jira")
        platform.connect()
        result = platform.create(
            project={"key": project},
            summary=summary,
            description=description,
            issuetype={"name": type},
        )
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("key")
@click.option("--summary", help="New summary")
@click.option("--description", help="New description")
def update(key, summary, description):
    """Update an issue."""
    try:
        platform = PlatformRegistry.get_platform("jira")
        platform.connect()
        fields = {}
        if summary:
            fields["summary"] = summary
        if description:
            fields["description"] = description
        platform.update(key, **fields)
        click.echo(f"Successfully updated issue {key}")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("key")
@click.argument("comment")
def comment(key, comment):
    """Add a comment to an issue."""
    try:
        platform = PlatformRegistry.get_platform("jira")
        platform.connect()
        result = platform.add_comment(key, comment)
        click.echo(f"Successfully added comment to issue {key}")
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@issue.command()
@click.argument("key")
@click.argument("status")
def status(key, status):
    """Update issue status."""
    try:
        platform = PlatformRegistry.get_platform("jira")
        platform.connect()
        platform.transition_status(key, status)
        click.echo(f"Successfully transitioned issue {key} to '{status}'")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)
