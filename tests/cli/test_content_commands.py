"""Tests for content-related CLI commands."""

import pytest
from click.testing import CliRunner
from pathlib import Path
from conduit.cli.main import cli
from conduit.core.config import Config, JiraConfig, ConfluenceConfig, SiteConfig


@pytest.fixture
def mock_config(tmp_path, monkeypatch):
    """Create a mock configuration for testing."""
    content_dir = tmp_path / "content"
    config = Config(
        jira=JiraConfig(
            default_site_alias="default",
            sites={"default": SiteConfig(url="", email="", api_token="")},
        ),
        confluence=ConfluenceConfig(url="", email="", api_token="", sites={}),
        content_dir=content_dir,
    )

    def mock_load_config():
        return config

    monkeypatch.setattr("conduit.cli.main.load_config", mock_load_config)
    return config


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


def test_get_content_path(cli_runner, mock_config):
    """Test getting a path for content storage."""
    result = cli_runner.invoke(cli, ["get-content-path"])
    assert result.exit_code == 0

    # Path should be absolute and end with .md
    path = Path(result.output.strip())
    assert path.is_absolute()
    assert path.suffix == ".md"
    assert not path.exists()  # Path should be generated but file not created
    assert path.parent == mock_config.content_dir


def test_create_issue_with_content_file(cli_runner, mock_config, monkeypatch):
    """Test creating an issue using a content file."""
    # Create a mock content file
    content = "Test description"
    content_file = mock_config.content_dir / "test.md"
    mock_config.content_dir.mkdir(exist_ok=True)
    content_file.write_text(content)

    # Mock the platform operations
    class MockPlatform:
        def connect(self):
            pass

        def create(self, **kwargs):
            assert kwargs["description"] == content
            assert kwargs["summary"] == "Test Issue"
            assert kwargs["project"]["key"] == "TEST"
            return {"key": "TEST-1"}

    def mock_get_platform(name, site_alias=None):
        return MockPlatform()

    monkeypatch.setattr(
        "conduit.platforms.registry.PlatformRegistry.get_platform", mock_get_platform
    )

    result = cli_runner.invoke(
        cli,
        [
            "jira",
            "issue",
            "create",
            "TEST",
            "--summary",
            "Test Issue",
            "--content-file",
            str(content_file),
        ],
    )

    assert result.exit_code == 0


def test_create_issue_nonexistent_content_file(cli_runner, mock_config):
    """Test creating an issue with a nonexistent content file."""
    result = cli_runner.invoke(
        cli,
        [
            "jira",
            "issue",
            "create",
            "TEST",
            "--summary",
            "Test Issue",
            "--content-file",
            "nonexistent.md",
        ],
    )

    # Click validates file existence and returns exit code 2 for invalid parameters
    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_create_issue_missing_required_options(cli_runner, mock_config):
    """Test creating an issue with missing required options."""
    # Missing --summary (using an existing file to avoid file existence check)
    test_file = mock_config.content_dir / "test.md"
    mock_config.content_dir.mkdir(exist_ok=True)
    test_file.touch()

    result1 = cli_runner.invoke(
        cli, ["jira", "issue", "create", "TEST", "--content-file", str(test_file)]
    )
    assert result1.exit_code == 2
    assert "Missing option" in result1.output
    assert "--summary" in result1.output

    # Missing --content-file
    result2 = cli_runner.invoke(
        cli, ["jira", "issue", "create", "TEST", "--summary", "Test Issue"]
    )
    assert result2.exit_code == 2
    assert "Missing option" in result2.output
    assert "--content-file" in result2.output


def test_update_issue_with_content_file(cli_runner, mock_config, monkeypatch):
    """Test updating an issue using a content file."""
    # Create a mock content file
    content = "Updated description"
    content_file = mock_config.content_dir / "update.md"
    mock_config.content_dir.mkdir(exist_ok=True)
    content_file.write_text(content)

    # Mock the platform operations
    class MockPlatform:
        def connect(self):
            pass

        def update(self, key, **kwargs):
            assert kwargs["description"] == content
            return None

    def mock_get_platform(name, site_alias=None):
        return MockPlatform()

    monkeypatch.setattr(
        "conduit.cli.commands.jira.PlatformRegistry.get_platform", mock_get_platform
    )

    result = cli_runner.invoke(
        cli,
        [
            "jira",
            "issue",
            "update",
            "TEST-1",
            "--content-file",
            str(content_file),
        ],
    )

    assert result.exit_code == 0
    assert "Successfully updated issue TEST-1" in result.output


def test_add_comment_missing_content_file(cli_runner, mock_config):
    """Test adding a comment without a content file."""
    result = cli_runner.invoke(cli, ["jira", "issue", "comment", "TEST-1"])
    assert result.exit_code == 2  # Click's error code for missing required option
    assert "Missing option" in result.output
    assert "--content-file" in result.output


def test_add_comment_with_content_file(cli_runner, mock_config, monkeypatch):
    """Test adding a comment using a content file."""
    # Create a mock content file
    content = "Test comment with formatting"
    content_file = mock_config.content_dir / "comment.md"
    mock_config.content_dir.mkdir(exist_ok=True)
    content_file.write_text(content)

    # Mock the platform operations
    class MockPlatform:
        def connect(self):
            pass

        def add_comment(self, key, comment):
            assert comment == content
            return {"id": "12345"}

    def mock_get_platform(name, site_alias=None):
        return MockPlatform()

    monkeypatch.setattr(
        "conduit.cli.commands.jira.PlatformRegistry.get_platform", mock_get_platform
    )

    result = cli_runner.invoke(
        cli,
        [
            "jira",
            "issue",
            "comment",
            "TEST-1",
            "--content-file",
            str(content_file),
        ],
    )

    assert result.exit_code == 0
    assert "Successfully added comment to issue TEST-1" in result.output
