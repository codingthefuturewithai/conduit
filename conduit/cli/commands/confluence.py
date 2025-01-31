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
