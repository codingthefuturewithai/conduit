import click

from conduit.core.exceptions import PlatformError
from conduit.platforms.registry import PlatformRegistry


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
@click.option("--site", help="Site alias to use for this operation")
def list(space, limit, site):
    """List pages in a Confluence space.

    Example: conduit confluence pages list SPACE --limit 20 [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("confluence", site_alias=site)
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
@click.option("--site", help="Site alias to use for this operation")
def content(space, format, depth, site):
    """Get content from a Confluence space.

    Format options:
      • clean: Formatted for AI/LLM consumption
      • storage: Raw Confluence storage format
      • raw: Unprocessed API response

    Example: conduit confluence pages content SPACE --format clean --depth all [--site site1]
    """
    try:
        platform = PlatformRegistry.get_platform("confluence", site_alias=site)
        platform.connect()
        content = platform.get_space_content(space, format=format, depth=depth)
        click.echo(content)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)


@pages.command()
@click.argument("space_key")
@click.option("--batch-size", default=100, help="Number of pages to fetch per request")
@click.option("--site", help="Site alias to use for this operation")
def list_all(space_key: str, batch_size: int, site: str):
    """List all pages in a space using pagination.

    Example: conduit confluence pages list-all SPACE --batch-size 100 [--site site1]
    """
    try:
        client = PlatformRegistry.get_platform("confluence", site_alias=site)
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
@click.option("--site", help="Site alias to use for this operation")
def children(parent_id: str, site: str):
    """List all child pages of a parent page.

    Example: conduit confluence pages children PAGE-ID [--site site1]
    """
    try:
        client = PlatformRegistry.get_platform("confluence", site_alias=site)
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
@click.argument("title")
@click.option("--format", default="clean", help="Output format: clean, storage, or raw")
@click.option("--site", help="Site alias to use for this operation")
def get(space_key: str, title: str, format: str, site: str):
    """Get a Confluence page by its title in a specific space.

    Retrieves a page using its title and space key. Since titles are unique within a space,
    this will return exactly one page if it exists.

    Format options:
      • clean: Formatted for AI/LLM consumption
      • storage: Raw Confluence storage format
      • raw: Unprocessed API response

    Example: conduit confluence pages get SPACE "Page Title" --format clean [--site site1]
    """
    try:
        client = PlatformRegistry.get_platform("confluence", site_alias=site)
        client.connect()

        if format not in ["clean", "storage", "raw"]:
            raise click.BadParameter('Format must be one of: "clean", "storage", "raw"')

        page = client.get_page_by_title(space_key, title)

        if not page:
            click.echo(f"No page found with title '{title}' in space {space_key}")
            return

        if format == "raw":
            click.echo(page)
            return

        if format == "clean":
            content = client.content_cleaner.clean(page["body"]["storage"]["value"])
        else:  # storage format
            content = page["body"]["storage"]["value"]

        click.echo(f"Title: {page['title']}")
        click.echo(f"ID: {page['id']}")
        click.echo(f"Version: {page['version']['number']}")
        click.echo(f"Last Updated: {page['version']['when']}")
        click.echo("\nContent:")
        click.echo(content)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        exit(1)
