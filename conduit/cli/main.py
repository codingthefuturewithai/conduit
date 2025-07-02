import functools
import logging
import sys

import click

from conduit.cli.commands.confluence import confluence
from conduit.cli.commands.jira import jira
from conduit.core.config import (create_default_config, get_config_dir,
                                 load_config)
from conduit.core.content import ContentManager
from conduit.core.exceptions import ConfigurationError
from conduit.core.logger import logger
from conduit.platforms.registry import PlatformRegistry


def handle_error(func):
    """Error handling decorator for CLI commands."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(str(e))
            sys.exit(1)

    return wrapper


def init_config():
    """Initialize the configuration file."""
    config_path = get_config_dir() / "config.yaml"
    if config_path.exists():
        logger.error(f"Configuration file already exists at {config_path}")
        logger.info("To start fresh, run: conduit config clean")
        sys.exit(1)
    try:
        create_default_config(config_path)
        logger.info(f"Configuration file created at: {config_path}")
        logger.info("\nPlease update it with your credentials:")
        logger.info(
            "1. Get API token: https://id.atlassian.com/manage-profile/security/api-tokens"
        )
        logger.info("2. Update URLs to match your Atlassian domain")
        logger.info("3. Set your email address")
    except ConfigurationError as e:
        logger.error(str(e))
        sys.exit(1)


class ConduitCLI(click.Group):
    """Custom Click Group that handles global flags without requiring commands."""

    def invoke(self, ctx):
        """Handle global flags before command processing."""
        if ctx.params.get("verbose"):
            logging.getLogger().setLevel(logging.INFO)
            logging.getLogger("conduit").setLevel(logging.DEBUG)
            logger.debug("Verbose logging enabled")

        if ctx.params.get("version"):
            import importlib.metadata

            try:
                version_str = importlib.metadata.version("conduit-connect")
                click.echo(f"Conduit version {version_str}")
            except importlib.metadata.PackageNotFoundError:
                click.echo("Conduit version unknown (package not installed)")
            sys.exit(0)

        if ctx.params.get("init"):
            init_config()
            sys.exit(0)

        return super().invoke(ctx)


@click.group(cls=ConduitCLI)
@click.option(
    "--verbose", is_flag=True, help="Enable verbose output for troubleshooting"
)
@click.option(
    "--init",
    is_flag=True,
    help="Initialize user configuration files in standard locations",
)
@click.option("--json", is_flag=True, help="Output results in JSON format")
@click.option("--version", is_flag=True, help="Show the version and exit")
def cli(verbose, init, json, version):
    """Conduit: Enterprise Knowledge Integration Service.

    A unified CLI for Jira and Confluence integration.

    Core Features:
      • Jira issue management and tracking
      • Confluence documentation access and search
      • Seamless platform integration
      • AI-optimized content formatting

    Configuration:
      • Linux/macOS: ~/.config/conduit/config.yaml
      • Windows: %APPDATA%\conduit\config.yaml

    Examples:
      Initialize configuration:
        $ conduit --init

      Test connection:
        $ conduit connect jira

      Create Jira issue:
        $ conduit jira issue create --project PROJ --summary "New Feature"

      Get Confluence content:
        $ conduit confluence pages content SPACE --format clean
    """
    pass


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
@handle_error
def clean():
    """Delete existing configuration file."""
    config_path = get_config_dir() / "config.yaml"
    if config_path.exists():
        config_path.unlink()
        logger.info(f"Deleted configuration file: {config_path}")
    else:
        logger.info("No configuration file found")


@config.command()
@click.option(
    "--platform",
    type=click.Choice(["jira", "confluence"]),
    help="Filter results by platform",
)
@handle_error
def list(platform):
    """List configured Atlassian sites.

    Shows all configured Jira and Confluence sites with their connection details.
    Sensitive information like API tokens is masked for security.

    Examples:
      $ conduit config list
      $ conduit config list --platform jira
      $ conduit config list --platform confluence
    """
    try:
        config = load_config()

        def format_site_info(platform_name, site_alias, site_config):
            return (
                f"  Site: {site_alias}\n"
                f"    URL: {site_config.url}\n"
                f"    Email: {site_config.email}\n"
                f"    API Token: ****"
            )

        if not platform or platform == "jira":
            click.echo("Platform: Jira")
            click.echo(f"Default Site: {config.jira.default_site_alias}")
            for site_alias, site_config in config.jira.sites.items():
                click.echo(format_site_info("Jira", site_alias, site_config))
            click.echo()

        if not platform or platform == "confluence":
            click.echo("Platform: Confluence")
            default_site = config.confluence.default_site_alias
            if default_site in config.confluence.sites:
                click.echo(f"Default Site: {default_site}")
            for site_alias, site_config in config.confluence.sites.items():
                click.echo(format_site_info("Confluence", site_alias, site_config))
            click.echo()

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


@cli.command()
@click.argument("platform_name", type=click.Choice(["jira", "confluence"]))
@click.option("--site", help="Site alias to use for this operation")
@handle_error
def connect(platform_name, site):
    """Test connection to a platform.

    Validates your credentials and connection settings for the specified platform.

    Examples:
      $ conduit connect jira
      $ conduit connect confluence --site site1
    """
    platform = PlatformRegistry.get_platform(platform_name, site_alias=site)
    platform.connect()
    logger.info(
        f"Successfully connected to {platform_name}"
        + (f" (site: {site})" if site else "")
    )


# Register platform-specific command groups
cli.add_command(jira)
cli.add_command(confluence)


@cli.command()
def get_content_path() -> None:
    """Get a path for storing formatted content.

    Returns an absolute path ending in .md that can be used to store any text-based content
    (not just markdown). The content format should match what the target system expects.

    The path will be within your configured content directory and have a unique name.
    You are responsible for writing content to this path.

    Example:
        $ path=$(conduit get-content-path)
        $ echo "# My Content" > "$path"
    """
    try:
        config = load_config()
        content_manager = ContentManager(config.get_content_dir())
        path = content_manager.generate_content_path()
        click.echo(str(path))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command(name="mcp")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option(
    "--transport",
    type=click.Choice(["sse", "stdio"]),
    default="stdio",
    help="Transport mode for MCP server (sse or stdio)",
)
def mcp_cmd(debug: bool, transport: str):
    """Start the Model Context Protocol server.

    This enables AI models to interact with Conduit through the MCP interface.
    """
    from conduit.mcp import main as mcp_main

    mcp_main(transport)


if __name__ == "__main__":
    cli()
