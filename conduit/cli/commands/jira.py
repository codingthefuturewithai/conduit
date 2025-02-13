import click
from conduit.platforms.registry import PlatformRegistry
from conduit.core.exceptions import PlatformError


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
@click.option("--project", required=True, help="Project key (e.g., PROJ)")
@click.option("--summary", required=True, help="Issue title/summary")
@click.option("--description", default="", help="Detailed issue description")
@click.option("--type", default="Task", help="Issue type (Task, Bug, Story, etc.)")
@click.option("--site", help="Site alias to use for this operation")
def create(project, summary, description, type, site):
    """Create a new Jira issue.

    Creates an issue with specified fields in the given project.
    Example: conduit jira issue create --project PROJ --summary "New Feature" --type Story [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
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
@click.option("--summary", help="New issue title/summary")
@click.option("--description", help="New issue description")
@click.option("--site", help="Site alias to use for this operation")
def update(key, summary, description, site):
    """Update an existing Jira issue's fields.

    Modify the summary and/or description of the specified issue.
    Example: conduit jira issue update PROJ-123 --summary "Updated Feature" [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
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
@click.option("--site", help="Site alias to use for this operation")
def comment(key, comment, site):
    """Add a comment to a Jira issue.

    Posts a new comment on the specified issue.
    Example: conduit jira issue comment PROJ-123 "Work in progress" [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("jira", site_alias=site)
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
