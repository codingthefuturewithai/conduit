import click
import functools
import logging
import sys
from pathlib import Path

from conduit.platforms.registry import PlatformRegistry
from conduit.core.exceptions import PlatformError, ConfigurationError
from conduit.cli.commands.jira import jira
from conduit.cli.commands.confluence import confluence
from conduit.core.config import (
    create_default_config,
    get_config_dir,
    load_config,
    SiteConfig,
)
from conduit.core.logger import logger


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
def cli(verbose, init, json):
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
            click.echo("Default Site Configuration:")
            click.echo(
                format_site_info(
                    "Confluence",
                    "default",
                    SiteConfig(
                        url=config.confluence.url,
                        email=config.confluence.email,
                        api_token="****",
                    ),
                )
            )
            if config.confluence.sites:
                click.echo("\nAdditional Sites:")
                for site_alias, site_config in config.confluence.sites.items():
                    click.echo(format_site_info("Confluence", site_alias, site_config))

    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


@cli.command()
@click.argument("platform_name", type=click.Choice(["jira", "confluence"]))
@handle_error
def connect(platform_name):
    """Test connection to a platform.

    Validates your credentials and connection settings for the specified platform.

    Examples:
      $ conduit connect jira
      $ conduit connect confluence
    """
    platform = PlatformRegistry.get_platform(platform_name)
    platform.connect()
    logger.info(f"Successfully connected to {platform_name}")


# Register platform-specific command groups
cli.add_command(jira)
cli.add_command(confluence)


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
