# Conduit - Enterprise Knowledge Integration Service

Conduit is a Python-based service designed to provide a unified, consistent interface for AI tools and applications to interact with enterprise knowledge and collaboration platforms. It currently supports Jira and Confluence integration.

## Features

- **Jira Integration**

  - Retrieve issues by key
  - Search issues using JQL
  - Create new issues
  - Update issue fields
  - Transition issue status

- **Confluence Integration**

  - List pages in a space with pagination
  - Get page content with formatting options
  - View child pages and hierarchies
  - Support for content cleaning and formatting
  - Rich text processing for AI consumption

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

confluence:
  url: "https://your-domain.atlassian.net"
  email: "your-email@example.com"
  api_token: "your-api-token"
```

To get your Atlassian API token:

1. Log in to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token and paste it in your config file

## Usage

### Command Line Interface

#### Jira Commands

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

6. Get remote links:

```bash
conduit jira issue remote-links PROJ-123
```

#### Confluence Commands

1. List pages in a space (limited number):

```bash
conduit confluence pages list SPACE --limit 10
```

2. List all pages in a space (with pagination):

```bash
conduit confluence pages list-all SPACE --batch-size 100
```

3. View child pages of a parent page:

```bash
conduit confluence pages children PAGE-ID
```

4. Get page content in raw storage format:

```bash
conduit confluence pages content SPACE
```

5. Get cleaned content (optimized for AI/LLM consumption):

```bash
conduit confluence pages content SPACE --format clean
```

6. Advanced content retrieval with options:

```bash
conduit confluence pages content SPACE \
  --depth all \
  --limit 10 \
  --expand "body.storage,version" \
  --format clean
```

### Python API

```python
from conduit import Conduit
from conduit.platforms.jira import JiraClient
from conduit.platforms.confluence import ConfluenceClient

# Initialize Jira client
jira = JiraClient()
jira.connect()

# Get an issue
issue = jira.get("PROJ-123")

# Search issues
issues = jira.search("project = PROJ AND status = 'In Progress'")

# Initialize Confluence client
confluence = ConfluenceClient()
confluence.connect()

# Get pages from a space
pages = confluence.get_pages_by_space("SPACE", limit=10)

# Get all pages with pagination
all_pages = confluence.get_all_pages_by_space("SPACE", batch_size=100)

# Get child pages
child_pages = confluence.get_child_pages("PAGE-ID")

# Get space content in raw format
content = confluence.get_space_content(
    "SPACE",
    depth="all",
    limit=500,
    expand="body.storage",
    format="storage"  # default
)

# Get space content in cleaned format (for AI/LLM)
content = confluence.get_space_content(
    "SPACE",
    depth="all",
    limit=500,
    expand="body.storage",
    format="clean"
)
```

The cleaned content format (`format="clean"`) provides:

- Preserved document structure
- Markdown-style formatting
- Cleaned HTML/XML markup
- Proper handling of:
  - Headers and sections
  - Lists and tables
  - Links and references
  - Code blocks
  - Task lists
  - Special Confluence elements

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
