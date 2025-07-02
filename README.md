# Conduit - Enterprise Knowledge Integration Service

[![PyPI version](https://badge.fury.io/py/conduit-connect.svg)](https://badge.fury.io/py/conduit-connect)

Conduit is a Python-based integration framework designed to provide a unified, consistent interface for AI tools and applications to interact with enterprise knowledge and collaboration platforms. Currently in an experimental stage and evolving rapidly, Conduit focuses on Atlassian tools (Jira and Confluence) as its initial integration targets. Our vision extends beyond just issue tracking and content management - over time,we plan to integrate with a broad ecosystem of development tools (like GitHub, Notion, Trello), knowledge bases, and productivity platforms to create a comprehensive bridge between AI assistants and your team's tools.

Conduit offers a full-featured command line interface and support for Anthropic's Model Context Protocol (MCP). While the CLI provides access to all of Conduit's capabilities, the MCP integration currently supports a focused set of core features. This allows for both comprehensive command-line usage and integration with AI tools that support MCP, such as Cursor and Claude Desktop.

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
  - Create new issues with markdown formatting
  - Update issues with formatted content
  - Add formatted comments
  - Transition issue status
  - View remote links
  - Automatic markdown to Jira format conversion
  - Sprint Management:
    - Get boards by project
    - Get sprints by board
    - Add issues to sprints

- **Content Management**

  - Get paths for storing formatted content
  - Support for standard markdown formatting
  - Automatic conversion to platform-specific formats
  - Clean separation of content and commands
  - Automatic cleanup of content files after successful operations
  - Failed content handling with dedicated storage
  - Content file support for:
    - Issue descriptions
    - Issue updates
    - Comments
    - Future platform content

- **Confluence Integration**

  - Multi-site support with site aliases
  - Hierarchical page retrieval with tree structure
  - Get page content with formatting options
  - Retrieve pages from space root or specific parent
  - Configurable depth and batch size limits
  - Support for content cleaning and formatting
  - Rich text processing for AI consumption
  - Create new pages with markdown content
  - Automatic markdown to Confluence storage format conversion
  - Support for parent-child page relationships
  - Image attachment support:
    - Attach images to new or existing pages
    - Embed attached images directly in page content
    - Automatic content type detection for attachments
    - Support for multiple attachments per operation

- **Configuration & Usability**

  - YAML-based configuration with multi-site support
  - Robust error handling
  - Detailed logging
  - Site alias management

- **MCP Integration** (Experimental)
  - Initial support for Anthropic's Model Context Protocol
  - Compatible with Cursor and Claude Desktop
  - Subset of features currently available via MCP
  - Ongoing development toward full feature parity

## Project Structure

```
conduit/
├── cli/                    # Command-line interface
│   └── commands/          # Platform-specific commands
├── config/                # Configuration management
├── core/                  # Core functionality
├── mcp/                   # Model Context Protocol implementation
└── platforms/             # Platform integrations
    ├── confluence/        # Confluence integration
    └── jira/              # Jira integration

tests/                     # Test suite
└── platforms/            # Platform integration tests

manual_testing/           # Manual testing resources
```

The project follows a modular architecture designed for extensibility:

- **CLI Layer**: Implements the command-line interface with platform-specific command modules
- **Configuration**: Handles YAML-based configuration with multi-site support
- **Core**: Provides shared utilities for configuration, logging, and error handling
- **MCP**: Implements the Model Context Protocol for AI tool integration
- **Platforms**: Contains platform-specific implementations with a common interface
  - Each platform is isolated in its own module
  - Platform-specific clients handle API interactions
  - Common interfaces ensure consistent behavior

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
pipx install conduit-connect
```

Windows:

```powershell
# Install pipx if not already installed
python -m pip install --user pipx
python -m pipx ensurepath

# Install conduit
pipx install conduit-connect
```

### Using uv (Alternative)

uv is a fast Python package installer and resolver.

macOS/Linux:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install conduit
uv pip install conduit-connect
```

Windows:

```powershell
# Install uv if not already installed
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install conduit
uv pip install conduit-connect
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
  default-site-alias: site1
  # Site configurations
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

To view your configured sites:

```bash
# List all configured sites
conduit config list

# Filter by platform
conduit config list --platform jira
conduit config list --platform confluence
```

Example output:

```text
Platform: Jira
Default Site: site1
  Site: site1
    URL: https://dev-domain.atlassian.net
    Email: dev@example.com
    API Token: ****
  Site: site2
    URL: https://staging-domain.atlassian.net
    Email: staging@example.com
    API Token: ****

Platform: Confluence
Default Site: site1
  Site: site1
    URL: https://dev-domain.atlassian.net
    Email: dev@example.com
    API Token: ****
  Site: site2
    URL: https://staging-domain.atlassian.net
    Email: staging@example.com
    API Token: ****
```

Configuration Management:

- Initialize config: `conduit --init`
- Delete config: `conduit config clean`
- List configured sites: `conduit config list [--platform jira|confluence]`
- Test connection:

```bash
# Test connection to default site
conduit connect jira

# Test connection to specific site
conduit connect confluence --site site1
```

Global Options:

- `--verbose`: Enable detailed logging for troubleshooting
- `--json`: Output results in JSON format
- `--init`: Initialize configuration file

## Content Handling

Conduit uses a file-based approach for handling formatted content (descriptions, comments, etc.) to ensure reliable formatting and proper conversion between different platforms. Instead of passing content directly as command arguments, Conduit follows a two-step process:

1. Get a path for storing content:

   ```bash
   path=$(conduit get-content-path)
   ```

   This generates a unique path in your configured content directory.

2. Write your content to the file:
   ```bash
   echo "Your formatted content" > "$path"
   ```
   The content can include markdown formatting which will be automatically converted to the appropriate format for each platform.

Benefits of this approach:

- Preserves complex formatting and multi-line content
- Avoids shell escaping issues
- Enables proper markdown conversion
- Provides automatic cleanup after successful operations
- Maintains failed content for debugging

Content files are automatically:

- Cleaned up after successful operations
- Moved to a `failed_content` directory if the operation fails
- Stored in your configured content directory (`~/.config/conduit/content` by default)

## Usage

### Command Line Interface

#### Configuration Commands

1. Initialize configuration:

```bash
conduit --init
```

2. List configured sites:

```bash
# List all configured sites
conduit config list

# List only Jira sites
conduit config list --platform jira

# List only Confluence sites
conduit config list --platform confluence
```

Example output:

```text
Platform: Jira
Default Site: site1
  Site: site1
    URL: https://dev-domain.atlassian.net
    Email: dev@example.com
    API Token: ****
  Site: site2
    URL: https://staging-domain.atlassian.net
    Email: staging@example.com
    API Token: ****

Platform: Confluence
Default Site: site1
  Site: site1
    URL: https://dev-domain.atlassian.net
    Email: dev@example.com
    API Token: ****
  Site: site2
    URL: https://staging-domain.atlassian.net
    Email: staging@example.com
    API Token: ****
```

3. Delete configuration:

```bash
conduit config clean
```

4. Test connection:

```bash
# Test connection to default site
conduit connect jira

# Test connection to specific site
conduit connect confluence --site site1
```

#### Working with Content Files

Conduit uses content files for handling formatted text (descriptions, comments, etc.). Always use this two-step process:

1. Get a path for your content:

```bash
content_path=$(conduit get-content-path)
```

2. Write your content to the file:

```bash
echo "Your formatted content" > "$content_path"
```

Note: Always use a unique variable name like `content_path` (not just `path`) to avoid shell environment conflicts.

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
# Get a path for your content
content_path=$(conduit get-content-path)

# Write your formatted content to the file
echo "# Description\n\nDetailed description with *markdown* formatting" > "$content_path"

# Create the issue using the content file
conduit jira issue create PROJ --summary "New Issue" --content-file "$content_path" --type Task [--site site1]
```

4. Update an issue:

```bash
# Update summary only
conduit jira issue update PROJ-123 --summary "Updated Summary" [--site site1]

# Update with formatted content
content_path=$(conduit get-content-path)
echo "# Updated Description\n\nNew formatted content" > "$content_path"
conduit jira issue update PROJ-123 --content-file "$content_path" [--site site1]

# Update both summary and content
conduit jira issue update PROJ-123 --summary "Updated Summary" --content-file "$content_path" [--site site1]
```

5. Add a comment:

```bash
# Get a path for your formatted comment
content_path=$(conduit get-content-path)

# Write your formatted comment to the file
echo "# Comment Title\n\n- Point 1\n- Point 2\n\n\`\`\`python\nprint('code example')\n\`\`\`" > "$content_path"

# Add the comment using the content file
conduit jira issue comment PROJ-123 --content-file "$content_path" [--site site1]
```

6. Transition issue status:

```bash
conduit jira issue status PROJ-123 "In Progress" [--site site1]
```

7. Get remote links:

```bash
conduit jira issue remote-links PROJ-123 [--site site1]
```

8. Sprint Management:

```bash
# Get boards for a project
conduit jira get-boards --project PROJ [--site site1]

# Get sprints for a board
conduit jira get-sprints BOARD-123 [--state active|future|closed] [--site site1]

# Add issues to a sprint
conduit jira add-to-sprint SPRINT-456 --issues PROJ-123 PROJ-124 [--site site1]
```

#### Confluence Commands

1. List pages in a space (limited number):

```bash
conduit confluence pages list SPACE --limit 10 [--site site1]
```

2. List all pages in a space (previously a flat list, now retrieves a hierarchy):

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

7. Retrieve Confluence page hierarchy: Retrieve a hierarchical tree of Confluence pages for a space, starting from the space root or a specific parent page. The result shows parent-child relationships, not just a flat list. You can limit the number of pages and the depth of the tree.

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

# Sprint Management
# Get boards for a project
boards = jira.get_boards(project_key="PROJ")

# Get sprints for a board
sprints = jira.get_sprints(board_id="BOARD-123", state="active")

# Add issues to a sprint
jira.add_issues_to_sprint(sprint_id="SPRINT-456", issue_keys=["PROJ-123", "PROJ-124"])

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

# Create a new page with markdown content
from conduit.core.services import ConfluenceService

# Create the page using markdown content
page = await ConfluenceService.create_page_from_markdown(
    space_key="SPACE",
    title="New Page Title",
    content="# Markdown Content\n\nThis is a page with **markdown** content",
    parent_id=None,  # Optional parent page ID
    site_alias=None  # Optional site alias
)

# Create a page with image attachments
attachments = [
    {"local_path": "/path/to/screenshot.png", "name_on_confluence": "app-screenshot.png"},
    {"local_path": "/path/to/diagram.jpg", "name_on_confluence": "architecture.jpg"}
]

# Content with embedded images (using Confluence storage format)
content_with_images = """
<h1>Page with Images</h1>
<p>Here's our application screenshot:</p>
<ac:image><ri:attachment ri:filename="app-screenshot.png" /></ac:image>
<p>And the architecture diagram:</p>
<ac:image><ri:attachment ri:filename="architecture.jpg" /></ac:image>
"""

page_with_images = await ConfluenceService.create_page_from_markdown(
    space_key="SPACE",
    title="Page with Embedded Images",
    content=content_with_images,
    attachments=attachments
)

# Update an existing page with new attachments
await ConfluenceService.update_page_from_markdown(
    space_key="SPACE",
    title="Existing Page",
    content=updated_content_with_images,
    expected_version=2,  # Current version number
    attachments=new_attachments,
    minor_edit=True  # Mark as minor edit to avoid notifications
)

# The returned page object contains:
# - id: The ID of the created page
# - title: The title of the page
# - space_key: The space key
# - url: Direct URL to the created page

# Conduit uses the md2cf library to convert markdown to Confluence storage format
# This supports standard markdown syntax including:
# - Headings, paragraphs, and text formatting
# - Lists (ordered and unordered)
# - Tables with formatting
# - Code blocks with syntax highlighting
# - Links and images
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

Conduit is designed to enhance AI coding assistants by providing them access to your organization's knowledge base. It supports two primary integration methods:

### 1. Model Context Protocol (MCP) - Experimental

Conduit provides support for Anthropic's Model Context Protocol, allowing integration with MCP-compatible AI tools. The MCP integration offers a focused set of core features, with ongoing development to expand the available capabilities. Current MCP support includes:

#### Currently Supported MCP Features

**Configuration**

- List all configured Jira and Confluence sites

**Confluence Operations**

- Get page content by title within a space
- List all pages in a space (previously a flat list, now retrieves a hierarchy)
- Retrieve Confluence page hierarchy: Retrieve a hierarchical tree of Confluence pages for a space, starting from the space root or a specific parent page. The result shows parent-child relationships, not just a flat list. You can limit the number of pages and the depth of the tree.
- Create new pages with markdown content (with optional parent page)
  - Automatically converts markdown to Confluence storage format
  - Supports standard markdown syntax including headings, lists, tables, and code blocks
  - Returns the created page URL for easy access
  - **NEW**: Attach images to pages during creation
  - **NEW**: Embed attached images using Confluence storage format
- Update existing pages with version conflict handling
  - **NEW**: Attach new images during page updates
  - Supports minor edits to avoid notification spam

**Jira Operations**

- Search issues using JQL syntax
- Create new issues (with summary, description, and issue type)
- Update existing issues (modify summary and description)
- Sprint management:
  - Get boards (optionally filtered by project)
  - Get sprints from boards (optionally filtered by state)
  - Add issues to sprints

#### Current MCP Limitations

- Limited to core read/write operations listed above
- Additional Confluence operations (like space content, child pages) only available via CLI, though creating pages from markdown is now fully supported
- Advanced Jira features (comments, transitions) only available via CLI
- Configuration changes must be done via CLI

#### Development and Testing with MCP Inspector

For development and testing, you can run the Conduit MCP server directly and explore its endpoints using the MCP Inspector:

1. After creating a venv and installing dependencies, start the MCP server in development mode:

   ```bash
   mcp dev conduit/mcp/server.py
   ```

2. Look for the MCP Inspector URL in the output:

   ```
   MCP Inspector is up and running at http://localhost:5173
   ```

3. Open the URL in your browser and click the "Connect" button to connect to the MCP server
4. Use the Inspector interface to explore available endpoints and test MCP functionality

#### Cursor Integration

1. First install Conduit following the [installation instructions above](#installation).

2. Get the full path to the MCP server:

```bash
which mcp-server-conduit
```

This will output something like `/Users/<username>/.local/bin/mcp-server-conduit`

3. Configure Cursor:
   - Open Cursor Settings > Features > MCP Servers
   - Click "+ Add New MCP Server"
   - Configure the server:
     - Name: conduit
     - Type: stdio
     - Command: [paste the full path from step 2]

For more details about MCP configuration in Cursor, see the [Cursor MCP documentation](https://docs.cursor.com/context/model-context-protocol).

#### Claude Desktop Integration

1. First install Conduit following the [installation instructions above](#installation).

2. Get the full path to the MCP server:

```bash
which mcp-server-conduit
```

This will output something like `/Users/<username>/.local/bin/mcp-server-conduit`

3. Configure Claude Desktop:
   - Open Claude menu > Settings > Developer > Edit Config
   - Add Conduit to the MCP servers configuration:

```json
{
  "mcpServers": {
    "conduit": {
      "command": "/Users/<username>/.local/bin/mcp-server-conduit"
    }
  }
}
```

For more details, see the [Claude Desktop MCP documentation](https://modelcontextprotocol.io/quickstart/user#for-claude-desktop-users).

### 2. Command Line Interface

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

## Checking Your Installed Version

To check which version of Conduit you have installed, run:

```bash
uv pip show conduit-connect
# or, if using pip:
pip show conduit-connect
```

This will display the installed version and other package details.

## Upgrading Conduit

To upgrade Conduit to the latest version, use the same tool you used to install it:

- If you used pip:
  ```sh
  pip install --upgrade conduit-connect
  ```

- If you used uv:
  ```sh
  uv pip install -U conduit-connect
  ```

- If you used pipx:
  ```sh
  pipx upgrade conduit-connect
  ```
