"""Tests for the content management functionality."""

import pytest
from pathlib import Path
from conduit.core.content import ContentManager


@pytest.fixture
def temp_content_dir(tmp_path):
    """Create a temporary directory for content files."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    return content_dir


@pytest.fixture
def content_manager(temp_content_dir):
    """Create a ContentManager instance with a temporary directory."""
    return ContentManager(temp_content_dir)


def test_content_manager_init(temp_content_dir):
    """Test ContentManager initialization."""
    manager = ContentManager(temp_content_dir)
    assert manager.content_dir == temp_content_dir
    assert temp_content_dir.exists()


def test_create_empty_content_file(content_manager):
    """Test creating an empty content file."""
    path = content_manager.generate_content_path()
    content_manager.write_content(path, "")
    assert path.exists()
    assert path.suffix == ".md"
    assert path.read_text() == ""


def test_create_content_file_with_content(content_manager):
    """Test creating a content file with initial content."""
    content = "# Test Content\n\nThis is a test."
    path = content_manager.generate_content_path()
    content_manager.write_content(path, content)
    assert path.exists()
    assert path.suffix == ".md"
    assert path.read_text() == content


def test_create_multiple_content_files(content_manager):
    """Test creating multiple content files creates unique files."""
    path1 = content_manager.generate_content_path()
    path2 = content_manager.generate_content_path()
    content_manager.write_content(path1, "content1")
    content_manager.write_content(path2, "content2")
    assert path1 != path2
    assert path1.exists() and path2.exists()
    assert path1.read_text() == "content1"
    assert path2.read_text() == "content2"


def test_generate_content_path(content_manager):
    """Test generating a content path."""
    path = content_manager.generate_content_path()
    assert path.is_absolute()
    assert path.suffix == ".md"
    assert not path.exists()  # Path should be generated but file not created
    assert path.parent == content_manager.content_dir


def test_generate_multiple_content_paths(content_manager):
    """Test generating multiple content paths creates unique paths."""
    path1 = content_manager.generate_content_path()
    path2 = content_manager.generate_content_path()
    assert path1 != path2
    assert path1.parent == path2.parent == content_manager.content_dir


def test_write_content(content_manager):
    """Test writing content to a file."""
    path = content_manager.generate_content_path()
    content = "Test content"
    content_manager.write_content(path, content)
    assert path.exists()
    assert path.read_text() == content


def test_write_content_outside_directory(content_manager, tmp_path):
    """Test writing content to a file outside content directory raises error."""
    outside_path = tmp_path / "outside.md"
    with pytest.raises(ValueError, match="File path must be within content directory"):
        content_manager.write_content(outside_path, "test content")


def test_read_content_existing_file(content_manager):
    """Test reading content from an existing file."""
    path = content_manager.generate_content_path()
    content = "Test content"
    content_manager.write_content(path, content)
    result = content_manager.read_content(path)
    assert result == content


def test_read_content_nonexistent_file(content_manager):
    """Test reading content from a nonexistent file raises error."""
    with pytest.raises(ValueError, match="Content file not found"):
        content_manager.read_content(Path("nonexistent.md"))


def test_content_dir_creation(tmp_path):
    """Test content directory is created if it doesn't exist."""
    content_dir = tmp_path / "nonexistent"
    manager = ContentManager(content_dir)
    assert content_dir.exists()
    assert content_dir.is_dir()


def test_cleanup_content_file(content_manager):
    """Test cleaning up a content file after successful processing."""
    path = content_manager.generate_content_path()
    content_manager.write_content(path, "test content")
    assert path.exists()
    content_manager.cleanup_content_file(path)
    assert not path.exists()


def test_cleanup_nonexistent_content_file(content_manager):
    """Test cleaning up a nonexistent content file."""
    path = content_manager.generate_content_path()
    content_manager.cleanup_content_file(path)  # Should not raise an error


def test_cleanup_content_file_outside_directory(content_manager, tmp_path):
    """Test cleaning up a file outside content directory raises error."""
    outside_path = tmp_path / "outside.md"
    with pytest.raises(ValueError, match="File path must be within content directory"):
        content_manager.cleanup_content_file(outside_path)


def test_mark_content_as_failed(content_manager):
    """Test marking a content file as failed."""
    path = content_manager.generate_content_path()
    content = "failed content"
    content_manager.write_content(path, content)
    assert path.exists()

    failed_path = content_manager.mark_content_as_failed(path)
    assert not path.exists()
    assert failed_path.exists()
    assert failed_path.parent == content_manager.failed_content_dir
    assert failed_path.read_text() == content


def test_mark_nonexistent_content_as_failed(content_manager):
    """Test marking a nonexistent content file as failed raises error."""
    path = content_manager.generate_content_path()
    with pytest.raises(ValueError, match="Content file not found"):
        content_manager.mark_content_as_failed(path)


def test_mark_content_as_failed_outside_directory(content_manager, tmp_path):
    """Test marking a file outside content directory as failed raises error."""
    outside_path = tmp_path / "outside.md"
    outside_path.write_text("test")
    with pytest.raises(ValueError, match="File path must be within content directory"):
        content_manager.mark_content_as_failed(outside_path)


def test_failed_content_directory_creation(tmp_path):
    """Test failed_content directory is created if it doesn't exist."""
    content_dir = tmp_path / "content"
    manager = ContentManager(content_dir)
    failed_dir = content_dir / "failed_content"
    assert failed_dir.exists()
    assert failed_dir.is_dir()
