import click
from typing import Optional

from conduit.platforms.registry import PlatformRegistry
from conduit.core.exceptions import PlatformError


@click.group()
def confluence():
    """Confluence documentation commands.

    Commands for managing Confluence content:
      • List and search pages
      • View page content
      • Export documentation
      • Access space content

    Requires Confluence credentials in ~/.config/conduit/config.yaml
    """
    pass


@confluence.group()
def pages():
    """Commands for working with Confluence pages.

    Supports operations like:
      • List pages in a space
      • Get page content
      • View page hierarchies
      • Export formatted content
    """
    pass


@pages.command()
@click.argument("space")
@click.option("--limit", default=10, help="Maximum number of pages to return")
def list(space, limit):
    """List pages in a Confluence space.

    Example: conduit confluence pages list SPACE --limit 20
    """
    try:
        platform = PlatformRegistry.get_platform("confluence")
        platform.connect()
        pages = platform.get_pages_by_space(space, limit=limit)
        click.echo(pages)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@pages.command()
@click.argument("space")
@click.option("--format", default="clean", help="Output format: clean, storage, or raw")
@click.option("--depth", default="root", help="Content depth: root, all, or children")
def content(space, format, depth):
    """Get content from a Confluence space.

    Format options:
      • clean: Formatted for AI/LLM consumption
      • storage: Raw Confluence storage format
      • raw: Unprocessed API response

    Example: conduit confluence pages content SPACE --format clean --depth all
    """
    try:
        platform = PlatformRegistry.get_platform("confluence")
        platform.connect()
        content = platform.get_space_content(space, format=format, depth=depth)
        click.echo(content)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


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
