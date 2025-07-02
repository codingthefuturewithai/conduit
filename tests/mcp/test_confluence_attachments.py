"""Tests for Confluence MCP tools with attachment support"""

from unittest.mock import patch

import pytest
from mcp.types import TextContent

from conduit.mcp.server import create_mcp_server


class TestConfluenceMCPAttachments:
    """Test cases for Confluence MCP tools with attachment functionality"""

    @pytest.fixture
    def mcp_server(self):
        """Create an MCP server instance for testing"""
        return create_mcp_server()

    @pytest.mark.asyncio
    async def test_create_page_with_attachments_tool(self, mcp_server):
        """Test create_confluence_page_from_markdown tool with attachments"""
        # Find the tool function
        tool = mcp_server._tool_manager.get_tool("create_confluence_page_from_markdown")
        assert tool is not None
        create_page_tool = tool.fn

        with patch(
            "conduit.core.services.ConfluenceService.create_page_from_markdown"
        ) as mock_create:
            # Mock successful page creation
            mock_create.return_value = {
                "id": "12345",
                "title": "Test Page with Images",
                "space_key": "TEST",
                "url": "https://test.atlassian.net/wiki/spaces/TEST/pages/12345",
                "version": 1,
                "response": {"id": "12345", "version": {"number": 1}},
            }

            # Test data
            attachments = [
                {
                    "local_path": "/tmp/image1.png",
                    "name_on_confluence": "screenshot1.png",
                },
                {"local_path": "/tmp/image2.jpg", "name_on_confluence": "diagram.jpg"},
            ]

            # Call the tool
            result = await create_page_tool(
                space="TEST",
                title="Test Page with Images",
                content='<p>Page with images</p><ac:image><ri:attachment ri:filename="screenshot1.png" /></ac:image>',
                attachments=attachments,
            )

            # Verify the result
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Page created successfully" in result[0].text
            assert "Successfully attached 2 file(s)" in result[0].text
            assert "screenshot1.png" in result[0].text
            assert "diagram.jpg" in result[0].text

            # Verify the service was called correctly
            mock_create.assert_called_once_with(
                space_key="TEST",
                title="Test Page with Images",
                content='<p>Page with images</p><ac:image><ri:attachment ri:filename="screenshot1.png" /></ac:image>',
                parent_id=None,
                site_alias=None,
                attachments=attachments,
            )

    @pytest.mark.asyncio
    async def test_update_page_with_attachments_tool(self, mcp_server):
        """Test update_confluence_page tool with attachments"""
        # Find the tool function
        tool = mcp_server._tool_manager.get_tool("update_confluence_page")
        assert tool is not None
        update_page_tool = tool.fn

        with patch(
            "conduit.core.services.ConfluenceService.update_page_from_markdown"
        ) as mock_update:
            # Mock successful page update
            mock_update.return_value = {
                "id": "12345",
                "title": "Updated Page",
                "space_key": "TEST",
                "url": "https://test.atlassian.net/wiki/spaces/TEST/pages/12345",
                "version": 3,
                "response": {
                    "id": "12345",
                    "version": {"number": 3, "when": "2024-01-15T10:00:00Z"},
                },
            }

            # Test data
            attachments = [
                {
                    "local_path": "/tmp/new_image.png",
                    "name_on_confluence": "updated_screenshot.png",
                }
            ]

            # Call the tool
            result = await update_page_tool(
                space_key="TEST",
                title="Updated Page",
                content='<p>Updated content</p><ac:image><ri:attachment ri:filename="updated_screenshot.png" /></ac:image>',
                expected_version=2,
                attachments=attachments,
            )

            # Verify the result
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Page Updated Successfully" in result[0].text
            assert "Successfully attached 1 file(s)" in result[0].text
            assert "updated_screenshot.png" in result[0].text

            # Verify the service was called correctly
            mock_update.assert_called_once_with(
                space_key="TEST",
                title="Updated Page",
                content='<p>Updated content</p><ac:image><ri:attachment ri:filename="updated_screenshot.png" /></ac:image>',
                expected_version=2,
                site_alias=None,
                minor_edit=False,
                attachments=attachments,
            )

    @pytest.mark.asyncio
    async def test_create_page_storage_format_detection(self, mcp_server):
        """Test that storage format content is detected and handled correctly"""
        # Find the tool function
        tool = mcp_server._tool_manager.get_tool("create_confluence_page_from_markdown")
        assert tool is not None
        create_page_tool = tool.fn

        with patch(
            "conduit.core.services.ConfluenceService.create_page_from_markdown"
        ) as mock_create:
            mock_create.return_value = {
                "id": "12345",
                "title": "Test Page",
                "space_key": "TEST",
                "url": "https://test.atlassian.net/wiki/spaces/TEST/pages/12345",
                "version": 1,
                "response": {"id": "12345", "version": {"number": 1}},
            }

            # Content with storage format tags
            storage_content = """<p>This is already storage format</p>
<ac:image><ri:attachment ri:filename="test.png" /></ac:image>
<p>More content</p>"""

            await create_page_tool(
                space="TEST", title="Test Page", content=storage_content
            )

            # Verify the content was passed through as-is (storage format detected)
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            assert call_args[1]["content"] == storage_content

    @pytest.mark.asyncio
    async def test_create_page_markdown_conversion(self, mcp_server):
        """Test that markdown content is converted properly"""
        # Find the tool function
        tool = mcp_server._tool_manager.get_tool("create_confluence_page_from_markdown")
        assert tool is not None
        create_page_tool = tool.fn

        with patch(
            "conduit.core.services.ConfluenceService.create_page_from_markdown"
        ) as mock_create:
            mock_create.return_value = {
                "id": "12345",
                "title": "Test Page",
                "space_key": "TEST",
                "url": "https://test.atlassian.net/wiki/spaces/TEST/pages/12345",
                "version": 1,
                "response": {"id": "12345", "version": {"number": 1}},
            }

            # Plain markdown content
            markdown_content = "# Heading\n\nThis is **bold** text"

            await create_page_tool(
                space="TEST", title="Test Page", content=markdown_content
            )

            # Verify markdown was passed (will be converted in service layer)
            mock_create.assert_called_once()
            call_args = mock_create.call_args
            assert call_args[1]["content"] == markdown_content

    @pytest.mark.asyncio
    async def test_error_handling_in_tools(self, mcp_server):
        """Test error handling in MCP tools"""
        # Find the tool function
        tool = mcp_server._tool_manager.get_tool("create_confluence_page_from_markdown")
        assert tool is not None
        create_page_tool = tool.fn

        with patch(
            "conduit.core.services.ConfluenceService.create_page_from_markdown"
        ) as mock_create:
            # Mock an error
            mock_create.side_effect = Exception("Failed to attach file: File not found")

            # Call the tool
            result = await create_page_tool(
                space="TEST",
                title="Test Page",
                content="Test content",
                attachments=[
                    {"local_path": "/nonexistent.png", "name_on_confluence": "test.png"}
                ],
            )

            # Verify error is handled gracefully
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Error creating Confluence page" in result[0].text
            assert "Failed to attach file" in result[0].text
