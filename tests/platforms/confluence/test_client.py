"""Tests for Confluence client image attachment functionality"""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest

from conduit.core.exceptions import PlatformError
from conduit.platforms.confluence.client import ConfluenceClient


class TestConfluenceClientAttachments:
    """Test cases for Confluence client attachment functionality"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing"""
        mock_site_config = Mock()
        mock_site_config.url = "https://test.atlassian.net"
        mock_site_config.email = "test@example.com"
        mock_site_config.api_token = "test-token"

        mock_confluence_config = Mock()
        mock_confluence_config.get_site_config.return_value = mock_site_config

        return mock_confluence_config

    @pytest.fixture
    def client(self, mock_config):
        """Create a Confluence client with mocked config"""
        with patch("conduit.platforms.confluence.client.load_config") as mock_load:
            mock_load.return_value.confluence = mock_config
            client = ConfluenceClient()
            client.confluence = Mock()
            return client

    def test_attach_file_success(self, client):
        """Test successful file attachment"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".png", delete=False) as tmp:
            tmp.write("test image content")
            tmp_path = tmp.name

        try:
            # Mock the confluence attach_file method
            expected_result = {
                "id": "att123",
                "title": "test_image.png",
                "metadata": {"mediaType": "image/png"},
            }
            client.confluence.attach_file.return_value = expected_result

            # Call attach_file
            result = client.attach_file(
                page_id="12345", file_path=tmp_path, attachment_name="test_image.png"
            )

            # Verify the result
            assert result == expected_result
            client.confluence.attach_file.assert_called_once_with(
                filename=tmp_path,
                name="test_image.png",
                page_id="12345",
                title=None,
                space=None,
                comment=None,
            )
        finally:
            # Clean up
            os.unlink(tmp_path)

    def test_attach_file_not_connected(self):
        """Test attach_file when not connected to Confluence"""
        with patch("conduit.platforms.confluence.client.load_config"):
            client = ConfluenceClient()
            client.confluence = None

            with pytest.raises(PlatformError, match="Not connected to Confluence"):
                client.attach_file(
                    page_id="12345",
                    file_path="/path/to/file.png",
                    attachment_name="file.png",
                )

    def test_attach_file_not_found(self, client):
        """Test attach_file with non-existent file"""
        with pytest.raises(FileNotFoundError, match="Local file not found"):
            client.attach_file(
                page_id="12345",
                file_path="/non/existent/file.png",
                attachment_name="file.png",
            )

    def test_attach_file_is_directory(self, client):
        """Test attach_file with directory instead of file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Path is not a file"):
                client.attach_file(
                    page_id="12345", file_path=tmpdir, attachment_name="file.png"
                )

    def test_attach_file_content_type_detection(self, client):
        """Test automatic content type detection"""
        test_cases = [
            (".png", "image/png"),
            (".jpg", "image/jpeg"),
            (".gif", "image/gif"),
            (".pdf", "application/pdf"),
            (".txt", "text/plain"),
            (".unknown", "application/octet-stream"),  # Default fallback
        ]

        for extension, expected_content_type in test_cases:
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
                tmp.write(b"test content")
                tmp_path = tmp.name

            try:
                # Mock successful upload
                client.confluence.attach_file.return_value = {"id": "att123"}

                # The content type is auto-detected internally but not passed to attach_file
                result = client.attach_file(
                    page_id="12345",
                    file_path=tmp_path,
                    attachment_name=f"test{extension}",
                )

                assert result == {"id": "att123"}
            finally:
                os.unlink(tmp_path)

    def test_attach_file_with_explicit_content_type(self, client):
        """Test attachment with explicitly provided content type"""
        with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as tmp:
            tmp.write(b"binary content")
            tmp_path = tmp.name

        try:
            client.confluence.attach_file.return_value = {"id": "att123"}

            result = client.attach_file(
                page_id="12345",
                file_path=tmp_path,
                attachment_name="custom.bin",
                content_type="application/custom-type",
            )

            assert result == {"id": "att123"}
        finally:
            os.unlink(tmp_path)

    def test_attach_file_api_error(self, client):
        """Test attach_file with API error"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        try:
            # Mock API error
            error = Exception("API Error: Attachment already exists")
            error.response = Mock()
            error.response.status_code = 409
            error.response.text = "Attachment with this name already exists"

            client.confluence.attach_file.side_effect = error

            with pytest.raises(PlatformError, match="Failed to attach file"):
                client.attach_file(
                    page_id="12345", file_path=tmp_path, attachment_name="duplicate.png"
                )
        finally:
            os.unlink(tmp_path)


class TestConfluenceServiceAttachments:
    """Test cases for Confluence service attachment functionality"""

    @pytest.mark.asyncio
    async def test_create_page_with_attachments(self):
        """Test creating a page with attachments"""
        from conduit.core.services import ConfluenceService

        with patch.object(ConfluenceService, "_get_client") as mock_get_client:
            # Setup mocks
            mock_client = Mock()
            mock_client.config = Mock()
            mock_client.config.get_site_config.return_value = Mock(
                url="https://test.atlassian.net"
            )
            mock_client.connect = Mock()
            mock_client.create_page = AsyncMock(
                return_value={"id": "123", "version": {"number": 1}}
            )
            mock_client.attach_file = Mock()

            mock_get_client.return_value = mock_client

            # Create temporary test image
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(b"test image")
                tmp_path = tmp.name

            try:
                # Test data
                attachments = [
                    {"local_path": tmp_path, "name_on_confluence": "test_image.png"}
                ]

                # Create page with attachments
                result = await ConfluenceService.create_page_from_markdown(
                    space_key="TEST",
                    title="Test Page with Image",
                    content='# Test\n\nContent with image: <ac:image><ri:attachment ri:filename="test_image.png" /></ac:image>',
                    attachments=attachments,
                )

                # Verify page was created
                assert result["id"] == "123"
                assert result["version"] == 1

                # Verify attachment was uploaded
                mock_client.attach_file.assert_called_once_with(
                    page_id="123", file_path=tmp_path, attachment_name="test_image.png"
                )
            finally:
                os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_update_page_with_attachments(self):
        """Test updating a page with new attachments"""
        from conduit.core.services import ConfluenceService

        with patch.object(ConfluenceService, "_get_client") as mock_get_client:
            # Setup mocks
            mock_client = Mock()
            mock_client.config = Mock()
            mock_client.config.get_site_config.return_value = Mock(
                url="https://test.atlassian.net"
            )
            mock_client.connect = Mock()
            mock_client.get_page_by_title = Mock(
                return_value={"id": "123", "version": {"number": 2}}
            )
            mock_client.confluence = Mock()
            mock_client.confluence.update_page = Mock(
                return_value={"id": "123", "version": {"number": 3}}
            )
            mock_client.attach_file = Mock()

            mock_get_client.return_value = mock_client

            # Create temporary test image
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                tmp.write(b"test image 2")
                tmp_path = tmp.name

            try:
                # Test data
                attachments = [
                    {"local_path": tmp_path, "name_on_confluence": "updated_image.jpg"}
                ]

                # Update page with attachments
                await ConfluenceService.update_page_from_markdown(
                    space_key="TEST",
                    title="Test Page",
                    content='# Updated\n\n<ac:image><ri:attachment ri:filename="updated_image.jpg" /></ac:image>',
                    expected_version=2,
                    attachments=attachments,
                )

                # Verify attachment was uploaded before page update
                mock_client.attach_file.assert_called_once_with(
                    page_id="123",
                    file_path=tmp_path,
                    attachment_name="updated_image.jpg",
                )

                # Verify page was updated
                assert mock_client.confluence.update_page.called
            finally:
                os.unlink(tmp_path)

    @pytest.mark.asyncio
    async def test_create_page_with_invalid_attachment(self):
        """Test creating a page with invalid attachment data"""
        from conduit.core.services import ConfluenceService

        with patch.object(ConfluenceService, "_get_client") as mock_get_client:
            # Setup mocks
            mock_client = Mock()
            mock_client.config = Mock()
            mock_client.config.get_site_config.return_value = Mock(
                url="https://test.atlassian.net"
            )
            mock_client.connect = Mock()
            mock_client.create_page = AsyncMock(
                return_value={"id": "123", "version": {"number": 1}}
            )
            mock_client.attach_file = Mock()

            mock_get_client.return_value = mock_client

            # Test data with invalid attachment (missing required fields)
            attachments = [
                {"local_path": "/some/path.png"},  # Missing name_on_confluence
                {"name_on_confluence": "test.png"},  # Missing local_path
            ]

            # Create page with invalid attachments
            result = await ConfluenceService.create_page_from_markdown(
                space_key="TEST",
                title="Test Page",
                content="# Test",
                attachments=attachments,
            )

            # Page should still be created
            assert result["id"] == "123"

            # No attachments should be uploaded (invalid data)
            mock_client.attach_file.assert_not_called()
