"""Content management module for handling formatted text content."""

import shutil
import uuid
from pathlib import Path

from conduit.core.logger import logger


class ContentManager:
    def __init__(self, content_dir: Path):
        """Initialize the content manager with a directory for storing content files.

        Args:
            content_dir: Path to the directory where content files will be stored
        """
        self.content_dir = content_dir
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.failed_content_dir = content_dir / "failed_content"
        self.failed_content_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Initialized ContentManager with directory: {content_dir}")

    def generate_content_path(self) -> Path:
        """Generate a new path for content storage.

        Returns:
            Path: The absolute path where content can be stored
        """
        file_id = str(uuid.uuid4())
        content_path = self.content_dir / f"{file_id}.md"
        logger.debug(f"Generated content path: {content_path}")
        return content_path.absolute()

    def write_content(self, file_path: Path, content: str) -> None:
        """Write content to a file.

        Args:
            file_path: Path to write the content to
            content: The content to write

        Raises:
            ValueError: If the file is not within the content directory
        """
        if not str(file_path.absolute()).startswith(str(self.content_dir.absolute())):
            raise ValueError(
                f"File path must be within content directory: {self.content_dir}"
            )

        logger.debug(f"Writing content to file: {file_path}")
        file_path.write_text(content)

    def read_content(self, file_path: Path) -> str:
        """Read content from a file.

        Args:
            file_path: Path to the content file to read

        Returns:
            str: The content of the file

        Raises:
            ValueError: If the file does not exist
        """
        if not file_path.exists():
            raise ValueError(f"Content file not found: {file_path}")

        logger.debug(f"Reading content from file: {file_path}")
        return file_path.read_text()

    def cleanup_content_file(self, file_path: Path) -> None:
        """Delete a content file after successful processing.

        Args:
            file_path: Path to the content file to delete

        Raises:
            ValueError: If the file is not within the content directory
        """
        if not str(file_path.absolute()).startswith(str(self.content_dir.absolute())):
            raise ValueError(
                f"File path must be within content directory: {self.content_dir}"
            )

        if file_path.exists():
            logger.debug(f"Cleaning up content file: {file_path}")
            file_path.unlink()

    def mark_content_as_failed(self, file_path: Path) -> Path:
        """Move a failed content file to the failed_content directory.

        Args:
            file_path: Path to the content file that failed processing

        Returns:
            Path: The new path of the file in the failed_content directory

        Raises:
            ValueError: If the file is not within the content directory
        """
        if not str(file_path.absolute()).startswith(str(self.content_dir.absolute())):
            raise ValueError(
                f"File path must be within content directory: {self.content_dir}"
            )

        if not file_path.exists():
            raise ValueError(f"Content file not found: {file_path}")

        failed_path = self.failed_content_dir / file_path.name
        logger.debug(f"Moving failed content file to: {failed_path}")
        shutil.move(str(file_path), str(failed_path))
        return failed_path
