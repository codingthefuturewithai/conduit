# Conduit - Enterprise Knowledge Integration Service

Conduit is a Python-based integration framework designed to provide a unified, consistent interface for AI tools and applications to interact with enterprise knowledge and collaboration platforms. Currently in an experimental stage and evolving rapidly, Conduit focuses on Atlassian tools (Jira and Confluence) as its initial integration targets. Our vision extends beyond just issue tracking and content management - over time,we plan to integrate with a broad ecosystem of development tools (like GitHub, Notion, Trello), knowledge bases, and productivity platforms to create a comprehensive bridge between AI assistants and your team's tools.

Although Conduit is currently only accessible via the command line, we plan to eventually expose it via other interfaces (such as Anthropics's Model Context Protocol and/or a REST API) for programmatic access and integration with AI assistants and other applications.

## Why Conduit?

Modern software development teams rely on an ever-growing array of specialized tools throughout their development lifecycle - from issue tracking and documentation to version control and CI/CD. While each tool excels at its specific purpose, the fragmentation between these tools creates significant friction:

- Developers constantly context-switch between different tools and environments
- Information is scattered across multiple platforms, making it hard to find and connect related content
- Copy-pasting between tools is error-prone and time-consuming
- AI assistants lack unified access to your team's knowledge and workflows
- Integration efforts are often manual and don't scale well

Conduit aims to solve these challenges by:

1. **Unified Access**: Creating a single, consistent interface to interact with all your development tools
2. **AI-First Design**: Making your tools' data and functionality readily available to AI assistants
3. **Seamless Integration**: Eliminating manual copying and context switching between tools
4. **Knowledge Connection**: Linking related information across different platforms automatically
5. **Workflow Automation**: Enabling automated workflows that span multiple tools

By bridging the gaps between your development tools and making them AI-accessible, Conduit helps teams stay focused on building great software rather than juggling tools.

## Features

- **Jira Integration**

  - Multi-site support with site aliases
  - Retrieve issues by key
  - Search issues using JQL
  - Create new issues
  - Update issue fields
  - Add comments to issues
  - Transition issue status
  - View remote links

- **Confluence Integration**

  - Multi-site support with site aliases
  - List pages in a space with pagination
  - Get page content with formatting options
  - View child pages and hierarchies
  - Support for content cleaning and formatting
  - Rich text processing for AI consumption

- **Configuration & Usability**
  - YAML-based configuration with multi-site support
  - Robust error handling
  - Detailed logging
  - Site alias management

## Project Structure

```
conduit/
├── cli/                    # Command-line interface
│   ├── commands/          # Platform-specific commands
│   │   ├── confluence.py  # Confluence CLI commands
│   │   └── jira.py       # Jira CLI commands
│   └── main.py           # CLI entry point and command routing
├── config/                # Configuration management
│   ├── config.yaml       # Default configuration template
│   └── __init__.py       # Configuration initialization
├── core/                  # Core functionality
│   ├── config.py         # Configuration loading and validation
│   ├── exceptions.py     # Custom exception definitions
│   └── logger.py         # Logging configuration
└── platforms/            # Platform integrations
    ├── base.py          # Base classes for platforms
    ├── registry.py      # Platform registration system
    ├── confluence/      # Confluence integration
    │   ├── client.py    # Confluence API client
    │   ├── config.py    # Confluence configuration
    │   └── content.py   # Content processing utilities
    └── jira/            # Jira integration
        ├── client.py    # Jira API client
        └── config.py    # Jira configuration

tests/                    # Test suite
└── platforms/           # Platform integration tests
    └── jira/            # Jira-specific tests

manual_testing/          # Manual testing resources
├── confluence_commands.md  # Confluence CLI examples
└── jira_commands.md       # Jira CLI examples
```

The project follows a modular architecture designed for extensibility:

- **CLI Layer**: Implements the command-line interface with platform-specific command modules
- **Configuration**: Handles YAML-based configuration with multi-site support
- **Core**: Provides shared utilities for configuration, logging, and error handling
- **Platforms**: Contains platform-specific implementations with a common interface
  - Each platform is isolated in its own module
  - `base.py` defines the common interface
  - `registry.py` enables dynamic platform registration
  - Platform-specific clients handle API interactions

## Installation

### Requirements

- Python 3.10 or higher (Python 3.12 is the latest supported version)
- pip, pipx, or uv package installer

### Using pipx (Recommended)

pipx provides isolated environments for Python applications, ensuring clean installation and easy updates.

macOS/Linux:

```bash
# Install pipx if not already installed
python -m pip install --user pipx
python -m pipx ensurepath

# Install conduit
pipx install conduit
```

Windows:

```powershell
# Install pipx if not already installed
python -m pip install --user pipx
python -m pipx ensurepath

# Install conduit
pipx install conduit
```

### Using uv (Alternative)

uv is a fast Python package installer and resolver.

macOS/Linux:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install conduit
uv pip install conduit
```

Windows:

```powershell
# Install uv if not already installed
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install conduit
uv pip install conduit
```

### Development Installation

For contributing or development:

```bash
# Clone the repository
git clone https://github.com/yourusername/conduit.git
cd conduit

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install --upgrade pip  # Ensure latest pip
pip install -e .  # Install the package in editable mode
```

The development dependencies will be installed automatically. If you need to install them manually:

```bash
pip install pytest black isort mypy ruff
```

Note: Make sure you're in the root directory of the project where `pyproject.toml` is located when running the installation commands.

## Configuration

Initialize the configuration file:

```bash
conduit --init
```

This will create a configuration file at:

- Linux/macOS: `~/.config/conduit/config.yaml`
- Windows: `%APPDATA%\conduit\config.yaml`

Example configuration with multi-site support:

```yaml
jira:
  # Default site configuration
  default-site-alias: site1
  # Additional site configurations
  sites:
    site1:
      url: "https://dev-domain.atlassian.net"
      email: "dev@example.com"
      api_token: "dev-api-token"
    site2:
      url: "https://staging-domain.atlassian.net"
      email: "staging@example.com"
      api_token: "staging-api-token"

confluence:
  # Default site configuration
  url: "https://your-domain.atlassian.net"
  email: "your-email@example.com"
  api_token: "your-api-token"
  # Additional site configurations
  sites:
    site1:
      url: "https://dev-domain.atlassian.net"
      email: "dev@example.com"
      api_token: "dev-api-token"
    site2:
      url: "https://staging-domain.atlassian.net"
      email: "staging@example.com"
      api_token: "staging-api-token"
```

To get your Atlassian API token:

1. Log in to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token and paste it in your config file

Configuration Management:

- Initialize config: `conduit --init`
- Delete config: `conduit config clean`
- Test connection: `conduit connect jira`

Global Options:

- `--verbose`: Enable detailed logging for troubleshooting
- `--json`: Output results in JSON format
- `--init`: Initialize configuration file

## Usage

### Command Line Interface

#### Jira Commands

1. Get an issue:

```bash
conduit jira issue get PROJ-123 [--site site1]
```

2. Search issues:

```bash
conduit jira issue search "project = PROJ AND status = 'In Progress'" [--site site1]
```

3. Create an issue:

```bash
conduit jira issue create --project PROJ --summary "New Issue" --description "Issue description" --type Task [--site site1]
```

4. Update an issue:

```bash
conduit jira issue update PROJ-123 --summary "Updated Summary" [--site site1]
```

5. Add a comment:

```bash
conduit jira issue comment PROJ-123 "Your comment text" [--site site1]
```

6. Transition issue status:

```bash
conduit jira issue status PROJ-123 "In Progress" [--site site1]
```

7. Get remote links:

```bash
conduit jira issue remote-links PROJ-123 [--site site1]
```

#### Confluence Commands

1. List pages in a space (limited number):

```bash
conduit confluence pages list SPACE --limit 10 [--site site1]
```

2. List all pages in a space (with pagination):

```bash
conduit confluence pages list-all SPACE --batch-size 100 [--site site1]
```

3. View child pages of a parent page:

```bash
conduit confluence pages children PAGE-ID [--site site1]
```

4. Get space content in clean format:

```bash
conduit confluence pages content SPACE --format clean [--site site1]
```

5. Get space content in storage format:

```bash
conduit confluence pages content SPACE --format storage [--site site1]
```

6. Get a specific page by title:

```bash
conduit confluence pages get SPACE "Page Title" --format clean [--site site1]
```

### Python API

```python
from conduit.platforms.jira import JiraClient
from conduit.platforms.confluence import ConfluenceClient

# Initialize Jira client with optional site alias
jira = JiraClient(site_alias="site1")  # or JiraClient() for default site
jira.connect()

# Get an issue
issue = jira.get("PROJ-123")

# Search issues
issues = jira.search("project = PROJ AND status = 'In Progress'")

# Initialize Confluence client with optional site alias
confluence = ConfluenceClient(site_alias="site1")  # or ConfluenceClient() for default site
confluence.connect()

# Get pages from a space
pages = confluence.get_pages_by_space("SPACE", limit=10)

# Get all pages with pagination
all_pages = confluence.get_all_pages_by_space("SPACE", batch_size=100)

# Get child pages
child_pages = confluence.get_child_pages("PAGE-ID")

# Get a specific page by title
page = confluence.get_page_by_title(
    "SPACE",
    "Page Title",
    expand="version,body.storage"  # optional
)

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

## AI Assistant Integration

Conduit is designed to enhance AI coding assistants by providing them access to your organization's knowledge base. For detailed instructions on integrating Conduit with your preferred AI assistant, visit our [AI Assistant Integration Guide](https://github.com/codingthefuturewithai/conduit/blob/main/docs/ai-assistant-integration.md).

Key integration capabilities:

- Semantic search across Jira and Confluence content
- Rich context retrieval for AI prompts
- Multi-site support for complex organizations
- Clean, AI-friendly content formatting

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
