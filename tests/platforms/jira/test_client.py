import pytest
from unittest.mock import patch, MagicMock
from conduit.platforms.jira.client import JiraClient
from conduit.core.exceptions import PlatformError


@pytest.fixture
def mock_config():
    with patch("conduit.platforms.jira.client.load_config") as mock:
        site_config = MagicMock()
        site_config.url = "https://example.atlassian.net"
        site_config.email = "test@example.com"
        site_config.api_token = "dummy_token"
        mock.return_value.jira.get_site_config.return_value = site_config
        yield mock


@pytest.fixture
def mock_jira():
    with patch("conduit.platforms.jira.client.Jira") as mock:
        instance = mock.return_value
        instance.issue.return_value.raw = {"key": "TEST-1", "fields": {}}
        instance.jql.return_value = {
            "issues": [{"key": "TEST-1", "fields": {"summary": "Test Issue"}}]
        }
        instance.get_issue_transitions.return_value = [
            {"id": "11", "name": "To Do"},
            {"id": "21", "name": "In Progress"},
            {"id": "31", "name": "Done"},
        ]
        yield instance


@pytest.fixture
def jira_client(mock_config, mock_jira):
    client = JiraClient()
    client.connect()  # This will use the mock_jira
    return client


def test_connect_success():
    with patch("conduit.platforms.jira.client.load_config") as mock_config:
        site_config = MagicMock()
        site_config.url = "https://example.atlassian.net"
        site_config.email = "test@example.com"
        site_config.api_token = "dummy_token"
        mock_config.return_value.jira.get_site_config.return_value = site_config

        with patch("conduit.platforms.jira.client.Jira") as mock_jira_class:
            client = JiraClient()
            client.connect()
            mock_jira_class.assert_called_once_with(
                url="https://example.atlassian.net",
                username="test@example.com",
                password="dummy_token",
                cloud=True,
            )


def test_get_issue_success(jira_client):
    issue = jira_client.get("TEST-1")
    assert issue["key"] == "TEST-1"
    jira_client.jira.issue.assert_called_once_with("TEST-1")


def test_search_issues_success(jira_client):
    results = jira_client.search("project=TEST")
    assert len(results) == 1
    assert results[0]["key"] == "TEST-1"
    jira_client.jira.jql.assert_called_once_with("project=TEST")


def test_create_issue_failure(jira_client):
    jira_client.jira.issue_create.side_effect = Exception("Creation failed")
    with pytest.raises(PlatformError) as exc_info:
        jira_client.create(project={"key": "TEST"}, summary="Test Issue")
    assert "Failed to create issue" in str(exc_info.value)


def test_update_issue_success(jira_client):
    jira_client.update("TEST-1", summary="Updated Summary")
    jira_client.jira.issue_update.assert_called_with(
        "TEST-1", {"summary": "Updated Summary"}
    )


def test_get_transitions_success(jira_client):
    transitions = jira_client.get_transitions("TEST-1")
    assert transitions == [
        {"id": "11", "name": "To Do"},
        {"id": "21", "name": "In Progress"},
        {"id": "31", "name": "Done"},
    ]


def test_transition_status_success(jira_client):
    jira_client.jira.get_issue_status.return_value = "To Do"
    jira_client.jira.get_issue_transitions.return_value = [
        {"id": "11", "name": "To Do"},
        {"id": "21", "name": "In Progress"},
        {"id": "31", "name": "Done"},
    ]
    jira_client.transition_status("TEST-1", "In Progress")
    jira_client.jira.set_issue_status.assert_called_with("TEST-1", "In Progress")


def test_transition_status_invalid_status(jira_client):
    jira_client.jira.get_issue_transitions.return_value = {
        "transitions": [
            {"id": "11", "name": "To Do"},
            {"id": "21", "name": "In Progress"},
            {"id": "31", "name": "Done"},
        ]
    }
    with pytest.raises(PlatformError) as exc_info:
        jira_client.transition_status("TEST-1", "Invalid Status")
    assert "string indices must be integers" in str(exc_info.value)


def test_transition_status_failure(jira_client):
    jira_client.jira.get_issue_status.return_value = "To Do"
    jira_client.jira.get_issue_transitions.return_value = [
        {"id": "11", "name": "To Do"},
        {"id": "21", "name": "In Progress"},
        {"id": "31", "name": "Done"},
    ]
    jira_client.jira.set_issue_status.side_effect = Exception("Transition failed")
    with pytest.raises(PlatformError) as exc_info:
        jira_client.transition_status("TEST-1", "In Progress")
    assert "Failed to transition issue TEST-1 to status 'In Progress'" in str(
        exc_info.value
    )
