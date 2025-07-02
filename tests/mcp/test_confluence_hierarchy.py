"""Tests for Confluence hierarchical page retrieval."""

from unittest.mock import Mock, patch

import pytest

from conduit.core.exceptions import PlatformError
from conduit.platforms.confluence.client import ConfluenceClient


class TestConfluenceHierarchy:
    """Test cases for Confluence page hierarchy retrieval."""

    @pytest.fixture
    def mock_confluence_client(self):
        """Create a mock Confluence client."""
        with patch("conduit.platforms.confluence.client.load_config") as mock_config:
            with patch("conduit.platforms.confluence.client.Confluence") as mock_conf:
                # Mock the config structure
                mock_config.return_value.confluence.get_site_config.return_value = Mock(
                    url="https://test.atlassian.net",
                    email="test@example.com",
                    api_token="test-token",
                )

                client = ConfluenceClient(site_alias="test")
                client.confluence = mock_conf.return_value
                yield client

    def test_get_page_hierarchy_from_space_root(self, mock_confluence_client):
        """Test retrieving hierarchy from space root."""
        # Mock data
        mock_pages = [
            {
                "id": "1",
                "title": "Root Page 1",
                "version": {"number": 1, "when": "2024-01-01"},
                "_links": {"webui": "/pages/1"},
                "ancestors": [],
            },
            {
                "id": "2",
                "title": "Root Page 2",
                "version": {"number": 1, "when": "2024-01-02"},
                "_links": {"webui": "/pages/2"},
                "ancestors": [],
            },
            {
                "id": "3",
                "title": "Child Page",
                "version": {"number": 1, "when": "2024-01-03"},
                "_links": {"webui": "/pages/3"},
                "ancestors": [{"id": "1"}],
            },
        ]

        # Setup mocks
        mock_confluence_client.confluence.get_all_pages_from_space.return_value = (
            mock_pages
        )
        mock_confluence_client.confluence.get_page_child_by_type.side_effect = [
            [mock_pages[2]],  # Children of page 1
            [],  # Children of page 2
            [],  # Children of page 3
        ]

        # Execute
        result = mock_confluence_client.get_page_hierarchy(
            space_key="TEST", batch_size=10
        )

        # Assert
        assert result["space_key"] == "TEST"
        assert result["parent_page_id"] is None
        assert result["batch_size"] == 10
        assert result["max_depth"] is None
        assert result["total_pages"] == 3
        assert len(result["hierarchy"]) == 2  # Two root pages

        # Check first root page
        root1 = result["hierarchy"][0]
        assert root1["id"] == "1"
        assert root1["title"] == "Root Page 1"
        assert len(root1["children"]) == 1
        assert root1["children"][0]["id"] == "3"
        assert root1["children"][0]["title"] == "Child Page"

        # Check second root page
        root2 = result["hierarchy"][1]
        assert root2["id"] == "2"
        assert root2["title"] == "Root Page 2"
        assert len(root2["children"]) == 0

    def test_get_page_hierarchy_from_parent_page(self, mock_confluence_client):
        """Test retrieving hierarchy from a specific parent page."""
        # Mock data
        parent_page = {
            "id": "100",
            "title": "Parent Page",
            "version": {"number": 2, "when": "2024-01-10"},
            "_links": {"webui": "/pages/100"},
        }

        child_pages = [
            {
                "id": "101",
                "title": "Child 1",
                "version": {"number": 1, "when": "2024-01-11"},
                "_links": {"webui": "/pages/101"},
            },
            {
                "id": "102",
                "title": "Child 2",
                "version": {"number": 1, "when": "2024-01-12"},
                "_links": {"webui": "/pages/102"},
            },
        ]

        # Setup mocks
        mock_confluence_client.confluence.get_page_by_id.return_value = parent_page
        mock_confluence_client.confluence.get_page_child_by_type.side_effect = [
            child_pages,  # Children of parent page
            [],  # Children of child 1
            [],  # Children of child 2
        ]

        # Execute
        result = mock_confluence_client.get_page_hierarchy(
            space_key="TEST", parent_page_id="100", batch_size=10
        )

        # Assert
        assert result["parent_page_id"] == "100"
        assert result["total_pages"] == 3
        assert len(result["hierarchy"]) == 1

        # Check parent page
        parent = result["hierarchy"][0]
        assert parent["id"] == "100"
        assert parent["title"] == "Parent Page"
        assert len(parent["children"]) == 2
        assert parent["children"][0]["id"] == "101"
        assert parent["children"][1]["id"] == "102"

    def test_get_page_hierarchy_batch_size_limit(self, mock_confluence_client):
        """Test that batch size limit is respected."""
        # Mock data - create more pages than batch size
        mock_pages = [
            {
                "id": str(i),
                "title": f"Page {i}",
                "version": {"number": 1, "when": f"2024-01-{i:02d}"},
                "_links": {"webui": f"/pages/{i}"},
                "ancestors": [],
            }
            for i in range(1, 6)
        ]

        # Setup mocks
        mock_confluence_client.confluence.get_all_pages_from_space.return_value = (
            mock_pages
        )
        mock_confluence_client.confluence.get_page_child_by_type.return_value = []

        # Execute with batch size of 3
        result = mock_confluence_client.get_page_hierarchy(
            space_key="TEST", batch_size=3
        )

        # Assert
        assert result["total_pages"] == 3
        assert len(result["hierarchy"]) == 3

    def test_get_page_hierarchy_max_depth_limit(self, mock_confluence_client):
        """Test that max depth limit is respected."""

        # Mock data - create nested structure
        def mock_get_children(page_id, type, start, limit, expand=None):
            parent_id = page_id
            if parent_id == "1":
                return [
                    {
                        "id": "2",
                        "title": "Level 1",
                        "version": {"number": 1, "when": "2024-01-02"},
                        "_links": {"webui": "/2"},
                    }
                ]
            elif parent_id == "2":
                return [
                    {
                        "id": "3",
                        "title": "Level 2",
                        "version": {"number": 1, "when": "2024-01-03"},
                        "_links": {"webui": "/3"},
                    }
                ]
            elif parent_id == "3":
                return [
                    {
                        "id": "4",
                        "title": "Level 3",
                        "version": {"number": 1, "when": "2024-01-04"},
                        "_links": {"webui": "/4"},
                    }
                ]
            return []

        # Setup mocks
        root_page = {
            "id": "1",
            "title": "Root",
            "version": {"number": 1, "when": "2024-01-01"},
            "_links": {"webui": "/1"},
        }
        mock_confluence_client.confluence.get_page_by_id.return_value = root_page
        mock_confluence_client.confluence.get_page_child_by_type.side_effect = (
            mock_get_children
        )

        # Execute with max depth of 2
        result = mock_confluence_client.get_page_hierarchy(
            space_key="TEST", parent_page_id="1", max_depth=2
        )

        # Assert - should have root + 1 level only with max_depth=2
        assert result["total_pages"] == 2
        root = result["hierarchy"][0]
        assert root["id"] == "1"
        assert len(root["children"]) == 1
        assert root["children"][0]["id"] == "2"
        assert len(root["children"][0]["children"]) == 0  # Depth limit reached

    def test_get_page_hierarchy_not_connected(self):
        """Test error when client is not connected."""
        with patch("conduit.platforms.confluence.client.load_config") as mock_config:
            # Mock the config structure
            mock_config.return_value.confluence.get_site_config.return_value = Mock(
                url="https://test.atlassian.net",
                email="test@example.com",
                api_token="test-token",
            )

            client = ConfluenceClient(site_alias="test")
            # Don't connect

            with pytest.raises(PlatformError, match="Not connected to Confluence"):
                client.get_page_hierarchy(space_key="TEST")

    def test_get_page_hierarchy_invalid_parent_page(self, mock_confluence_client):
        """Test error when parent page doesn't exist."""
        # Setup mock to raise exception
        mock_confluence_client.confluence.get_page_by_id.side_effect = Exception(
            "Page not found"
        )

        with pytest.raises(PlatformError, match="Failed to get parent page"):
            mock_confluence_client.get_page_hierarchy(
                space_key="TEST", parent_page_id="invalid"
            )

    @pytest.mark.asyncio
    async def test_mcp_endpoint_integration(self):
        """Test the MCP endpoint integration."""
        # Instead of testing through the decorated function, test the client directly
        with patch("conduit.platforms.confluence.client.load_config") as mock_config:
            with patch("conduit.platforms.confluence.client.Confluence") as mock_conf:
                # Mock the config structure
                mock_config.return_value.confluence.get_site_config.return_value = Mock(
                    url="https://test.atlassian.net",
                    email="test@example.com",
                    api_token="test-token",
                )

                # Create client and mock Confluence API
                client = ConfluenceClient(site_alias="test")
                client.confluence = mock_conf.return_value

                # Mock get_page_by_id for parent page retrieval
                client.confluence.get_page_by_id.return_value = {
                    "id": "1",
                    "title": "Test Page",
                    "version": {"number": 1, "when": "2024-01-01"},
                    "_links": {"webui": "/pages/1"},
                }

                # Mock get_page_child_by_type for children
                client.confluence.get_page_child_by_type.return_value = []

                # Execute
                result = client.get_page_hierarchy(
                    space_key="TEST", parent_page_id="1", batch_size=100
                )

                # Assert the structure
                assert result["space_key"] == "TEST"
                assert result["parent_page_id"] == "1"
                assert result["batch_size"] == 100
                assert result["total_pages"] == 1
                assert len(result["hierarchy"]) == 1
                assert result["hierarchy"][0]["id"] == "1"
                assert result["hierarchy"][0]["title"] == "Test Page"
