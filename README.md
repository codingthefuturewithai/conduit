# Conduit - Enterprise Knowledge Integration Service

Conduit is a Python-based service designed to provide a unified, consistent interface for AI tools and applications to interact with enterprise knowledge and collaboration platforms. The MVP focuses on Jira integration with plans to expand to other platforms.

## Features

- **Jira Integration**

  - Retrieve issues by key
  - Search issues using JQL
  - Create new issues
  - Update issue fields
  - Transition issue status

- **Configuration & Usability**
  - YAML-based configuration
  - Robust error handling
  - Detailed logging

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/conduit.git
cd conduit
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:

```bash
pip install -e .
```

## Configuration

Create a configuration file at `~/.config/conduit/config.yaml`:

```yaml
jira:
  url: "https://your-domain.atlassian.net"
  email: "your-email@example.com"
  api_token: "your-api-token"
```

To get your Jira API token:

1. Log in to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token and paste it in your config file

## Usage

### Command Line Interface

1. Get an issue:

```bash
conduit jira issue get PROJ-123
```

2. Search issues:

```bash
conduit jira issue search "project = PROJ AND status = 'In Progress'"
```

3. Create an issue:

```bash
conduit jira issue create --project PROJ --summary "New Issue" --description "Issue description" --type Task
```

4. Update an issue:

```bash
conduit jira issue update PROJ-123 --summary "Updated Summary"
```

5. Transition issue status:

```bash
conduit jira issue status PROJ-123 "In Progress"
```

### Python API

```python
from conduit import Conduit
from conduit.platforms.jira import JiraClient

# Initialize client
client = JiraClient()
client.connect()

# Get an issue
issue = client.get("PROJ-123")

# Search issues
issues = client.search("project = PROJ AND status = 'In Progress'")

# Create an issue
new_issue = client.create(
    project={"key": "PROJ"},
    summary="New Issue",
    description="Issue description",
    issuetype={"name": "Task"}
)

# Update an issue
client.update("PROJ-123", summary="Updated Summary")

# Transition issue status
client.transition_status("PROJ-123", "In Progress")
```

## Development

1. Install development dependencies:

```bash
pip install -e ".[dev]"
```

2. Run tests:

```bash
pytest
```

3. Format code:

```bash
black .
isort .
```

4. Run type checking:

```bash
mypy .
```

## Future Enhancements

- REST API for programmatic access
- Additional platform integrations:
  - Confluence
  - Notion
  - Trello
  - GitHub
  - Google Docs
- Enhanced authentication & security
- Batch operations
- Additional output formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
