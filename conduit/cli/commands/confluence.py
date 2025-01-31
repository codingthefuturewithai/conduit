import click
from typing import Optional

from conduit.platforms.registry import PlatformRegistry
from conduit.core.exceptions import PlatformError


@click.group()
def confluence():
    """Confluence commands."""
    pass


@confluence.group()
def pages():
    """Manage Confluence pages."""
    pass


@pages.command()
@click.argument("space_key")
@click.option("--limit", default=100, help="Maximum number of pages to return")
def list(space_key: str, limit: int):
    """List pages in a space (limited to specified number)."""
    try:
        client = PlatformRegistry.get_platform("confluence")
        client.connect()
        pages = client.get_pages_by_space(space_key, limit)

        if not pages:
            click.echo(f"No pages found in space {space_key}")
            return

        click.echo(f"\nPages in space {space_key}:")
        for page in pages:
            click.echo(f"- {page['title']} (ID: {page['id']})")
    except PlatformError as e:
        click.echo(f"Error: {str(e)}", err=True)


@pages.command()
@click.argument("space_key")
@click.option("--batch-size", default=100, help="Number of pages to fetch per request")
def list_all(space_key: str, batch_size: int):
    """List all pages in a space using pagination."""
    try:
        client = PlatformRegistry.get_platform("confluence")
        client.connect()

        click.echo(f"Fetching all pages from space {space_key}...")
        pages = client.get_all_pages_by_space(space_key, batch_size=batch_size)

        if not pages:
            click.echo(f"No pages found in space {space_key}")
            return

        click.echo(f"\nFound {len(pages)} pages in space {space_key}:")
        for page in pages:
            click.echo(f"- {page['title']} (ID: {page['id']})")
    except PlatformError as e:
        click.echo(f"Error: {str(e)}", err=True)


@pages.command()
@click.argument("parent_id")
def children(parent_id: str):
    """List all child pages of a parent page."""
    try:
        client = PlatformRegistry.get_platform("confluence")
        client.connect()
        pages = client.get_child_pages(parent_id)

        if not pages:
            click.echo(f"No child pages found for parent {parent_id}")
            return

        click.echo(f"\nChild pages of {parent_id}:")
        for page in pages:
            click.echo(f"- {page['title']} (ID: {page['id']})")
    except PlatformError as e:
        click.echo(f"Error: {str(e)}", err=True)


@pages.command()
@click.argument("space_key")
@click.option("--depth", default="all", help="Depth of the content tree to return")
@click.option("--start", default=0, help="Start index for pagination")
@click.option("--limit", default=500, help="Maximum number of items to return")
@click.option(
    "--expand",
    default="body.storage",
    help="Comma-separated list of properties to expand",
)
@click.option(
    "--format",
    default="storage",
    type=click.Choice(["storage", "clean"]),
    help="Content format to return",
)
def content(
    space_key: str,
    depth: str,
    start: int,
    limit: int,
    expand: str,
    format: str,
):
    """Show detailed content of pages in a space."""
    try:
        client = PlatformRegistry.get_platform("confluence")
        client.connect()

        click.echo(f"Fetching content from space {space_key}...")
        content = client.get_space_content(
            space_key,
            depth=depth,
            start=start,
            limit=limit,
            expand=expand,
            format=format,
        )

        if not content or not content.get("page", {}).get("results"):
            click.echo(f"No content found in space {space_key}")
            return

        pages = content["page"]["results"]
        click.echo(f"\nFound {len(pages)} pages in space {space_key}:")

        for page in pages:
            click.echo(f"\n=== {page['title']} (ID: {page['id']}) ===")
            if format == "clean" and "body" in page and "clean" in page["body"]:
                click.echo("Content:")
                click.echo(page["body"]["clean"])
            elif "body" in page and "storage" in page["body"]:
                click.echo("Content:")
                click.echo(page["body"]["storage"]["value"])
            else:
                click.echo("(No content available)")
            click.echo("=" * (len(page["title"]) + 10))  # Add separator line

    except PlatformError as e:
        click.echo(f"Error: {str(e)}", err=True)
