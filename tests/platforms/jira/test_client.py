import pytest
from unittest.mock import patch, MagicMock
from conduit.platforms.jira.client import JiraClient
from conduit.core.exceptions import PlatformError

@pytest.fixture
def mock_config():
    with patch('conduit.platforms.jira.client.load_config') as mock:
        mock.return_value.jira.url = 'https://example.atlassian.net'
        mock.return_value.jira.api_token = 'dummy_token'
        yield mock

@pytest.fixture
def jira_client(mock_config):
    client = JiraClient()
    with patch('conduit.platforms.jira.client.Jira') as MockJira:
        client.jira = MockJira.return_value
        yield client

def test_connect_success(jira_client):
    with patch('conduit.platforms.jira.client.load_config') as mock_load_config:
        mock_load_config.return_value.jira.url = 'https://example.atlassian.net'
        mock_load_config.return_value.jira.api_token = 'dummy_token'
        jira_client.connect()
        jira_client.jira.assert_called_with(
            url='https://example.atlassian.net',
            token='dummy_token'
        )

def test_get_issue_success(jira_client):
    jira_client.jira.issue.return_value.raw = {'key': 'TEST-1', 'fields': {}}
    issue = jira_client.get('TEST-1')
    assert issue['key'] == 'TEST-1'

def test_search_issues_success(jira_client):
    jira_client.jira.jql.return_value = {
        'issues': [
            {'key': 'TEST-1', 'fields': {'summary': 'Test Issue'}}
        ]
    }
    results = jira_client.search('project=TEST')
    assert len(results) == 1
    assert results[0]['key'] == 'TEST-1'

def test_create_issue_failure(jira_client):
    jira_client.jira.create_issue.side_effect = Exception('Creation failed')
    with pytest.raises(PlatformError) as exc_info:
        jira_client.create(summary='Test Issue')
    assert 'Failed to create issue' in str(exc_info.value)

def test_update_issue_success(jira_client):
    jira_client.update('TEST-1', summary='Updated Summary')
    jira_client.jira.update_issue.assert_called_with('TEST-1', fields={'summary': 'Updated Summary'})
