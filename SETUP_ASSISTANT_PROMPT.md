# Conduit MCP Server Setup Assistant

This file contains instructions for AI coding assistants to help users set up the Conduit MCP (Model Context Protocol) server, enabling AI-powered integration with Atlassian tools (Jira and Confluence).

---

## To the AI Assistant

You are helping a user set up Conduit's MCP server so their AI coding assistant can interact with Atlassian tools. This is NOT about Conduit's command-line interface - it's specifically about getting the MCP server working with their AI assistant.

### Important Security Note
**NEVER** ask for or handle API tokens. The user will add their API token manually after you've completed the initial setup.

### Setup Goals
1. Install Conduit package
2. Configure Atlassian site information (URL and email only)
3. Set up MCP server in their AI coding assistant
4. Verify everything works through the AI assistant (not command line)

### Important Notes
- All testing and verification will be done through the AI assistant after MCP setup
- Conduit has a Streamlit-based admin UI that has known limitations on Windows, but this doesn't affect MCP functionality
- Users can install Conduit using pipx (recommended), uv, or pip
- You will help with everything EXCEPT the API token

## Prerequisites Check

First, determine the user's environment and available tools:

1. **Operating System Detection**:
   ```bash
   # Check OS type
   if [[ "$OSTYPE" == "linux-gnu"* ]]; then
       echo "Linux detected"
   elif [[ "$OSTYPE" == "darwin"* ]]; then
       echo "macOS detected"
   elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
       echo "Windows detected"
   fi
   
   # Alternative for cross-platform
   python -c "import platform; print(f'OS: {platform.system()}')"
   ```

2. **Python Version Check**:
   ```bash
   python --version || python3 --version
   ```
   - Conduit requires Python 3.10 or higher (supports up to 3.12)

3. **Package Manager Detection**:
   ```bash
   # Check for pipx
   pipx --version 2>/dev/null && echo "pipx is installed"
   
   # Check for uv
   uv --version 2>/dev/null && echo "uv is installed"
   
   # Check for pip
   pip --version 2>/dev/null && echo "pip is installed"
   ```

4. **Ask User Preference**:
   - "Which package manager would you prefer to use for installing Conduit?"
   - If they have multiple options, explain:
     - **pipx** (recommended): Provides isolated environment, easy updates
     - **uv**: Fast installation, modern Python package manager
     - **pip**: Traditional option, but may have dependency conflicts

## Installation Steps

### Step 1: Install Conduit

Based on the user's preference and available tools:

#### Option A: Using pipx (Recommended)

**macOS/Linux:**
```bash
# Install pipx if not already installed
python -m pip install --user pipx
python -m pipx ensurepath

# You may need to restart your terminal or run:
source ~/.bashrc  # or ~/.zshrc on macOS

# Install conduit
pipx install conduit-connect
```

**Windows:**
```powershell
# Install pipx if not already installed
python -m pip install --user pipx
python -m pipx ensurepath

# Restart your terminal, then:
pipx install conduit-connect
```

#### Option B: Using uv

**macOS/Linux:**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install conduit
uv pip install conduit-connect
```

**Windows:**
```powershell
# Install uv if not already installed
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install conduit
uv pip install conduit-connect
```

#### Option C: Using pip

```bash
# Not recommended for global installation
pip install conduit-connect
```

### Step 2: Verify Installation and Get MCP Server Path

```bash
# Get the path to the MCP server (critical for MCP setup)
which mcp-server-conduit  # macOS/Linux
where mcp-server-conduit  # Windows
```

Save the full path from the above command - this is the most important piece of information for MCP configuration.

### Step 3: Initialize Configuration

```bash
conduit --init
```

This creates a configuration file at:
- **Linux/macOS**: `~/.config/conduit/config.yaml`
- **Windows**: `%APPDATA%\conduit\config.yaml`

### Step 4: Configure Atlassian Site Information

Now we need to gather information about the user's Atlassian site:

1. **Ask for Atlassian URL**:
   "What is your Atlassian site URL? (e.g., https://mycompany.atlassian.net)"

2. **Ask for Email**:
   "What email address do you use to log into Atlassian?"

3. **Ask for Site Alias** (optional):
   "What would you like to call this site configuration? (default: 'default')"
   Explain: "This is just a nickname for your configuration, useful if you have multiple Atlassian sites"

4. **Update the Configuration File**:
   
   Once you have this information, update their config.yaml file:
   
   ```yaml
   jira:
     default-site-alias: mycompany  # Use their chosen alias
     sites:
       mycompany:  # Use the same alias here
         url: "https://their-domain.atlassian.net"  # Their actual URL
         email: "their-email@company.com"  # Their actual email
         api_token: ""  # Leave empty - user will add later
   
   confluence:
     default-site-alias: mycompany  # Usually same as Jira
     sites:
       mycompany:  # Use the same alias here
         url: "https://their-domain.atlassian.net"  # Usually same as Jira URL
         email: "their-email@company.com"  # Their actual email
         api_token: ""  # Leave empty - user will add later
   
   content_dir: ~/.config/conduit/content  # Leave as default
   ```

5. **Multi-Site Configuration** (if needed):
   
   If the user mentions having multiple Atlassian sites, help them add more:
   
   ```yaml
   jira:
     default-site-alias: production
     sites:
       production:
         url: "https://prod.atlassian.net"
         email: "user@company.com"
         api_token: ""  # User will add later
       staging:
         url: "https://staging.atlassian.net"
         email: "user@company.com"
         api_token: ""  # User will add later
   ```

### Step 5: API Token Instructions

After updating the configuration file, provide these instructions to the user:

**IMPORTANT - Manual Step Required**

"I've updated your configuration file with your Atlassian site information. Now you need to add your API token manually:

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click 'Create API token'
3. Give it a descriptive name (e.g., 'Conduit Integration')
4. Copy the token immediately (it won't be shown again)
5. Open your config file at: [show the path based on their OS]
6. Find the `api_token: ""` lines and paste your token between the quotes
7. Save the file

Once you've added your API token, we can proceed with testing the connection."

### Step 6: Prepare for MCP Configuration

Wait for user confirmation that they've added their API token, then proceed directly to MCP setup.

Note: We'll verify everything is working through the AI assistant after MCP is configured - no command-line testing needed.

### Step 7: Configure AI Assistant MCP Integration

Determine which AI assistant the user is using:

#### For Claude Code (Recommended Method):

1. Get the MCP server path (from Step 2):
   ```bash
   which mcp-server-conduit  # Save this path
   ```

2. **Windows Note**: Inform the user:
   > "Note: The Conduit admin UI has known limitations on Windows, but this doesn't affect the core MCP functionality you'll be using."

3. Use the claude mcp add-json command to add Conduit:
   ```bash
   # The exact path will vary based on OS and installation method
   # Common paths:
   # macOS with Homebrew: /opt/homebrew/bin/mcp-server-conduit
   # macOS/Linux with pipx: ~/.local/bin/mcp-server-conduit
   # Windows with pipx: C:\Users\[username]\AppData\Roaming\Python\Scripts\mcp-server-conduit.exe
   
   claude mcp add-json -s user Conduit '{"type":"stdio","command":"[YOUR_PATH_HERE]"}'
   ```
   
   Replace `[YOUR_PATH_HERE]` with the actual path from the `which` command.

#### For Claude Desktop:

1. Get the MCP server path (from Step 2)
2. Direct user to configure Claude:
   - Open Claude Desktop
   - Go to: Claude menu > Settings > Developer > Edit Config
   - Add Conduit to the configuration:
   
   ```json
   {
     "mcpServers": {
       "conduit": {
         "command": "/path/from/step1/mcp-server-conduit"
       }
     }
   }
   ```

#### For Cursor:

1. Get the MCP server path (from Step 2)

2. Direct user to configure Cursor using the GUI:
   - Open Cursor Settings (Cmd/Ctrl + ,)
   - Navigate to: Cursor Settings > Features > MCP Tools
   - You'll see the list of enabled MCP servers
   - Click the "+ New MCP Server" button at the bottom
   - This opens the configuration file

3. Add Conduit to the configuration:
   ```json
   {
     "Conduit": {
       "command": "/opt/homebrew/bin/mcp-server-conduit"
     }
   }
   ```
   
   Note: The server name MUST be "Conduit" with a capital C for proper recognition.

4. The configuration file location is:
   - macOS/Linux: `~/.cursor/mcp.json`
   - Windows: `%USERPROFILE%\.cursor\mcp.json`

#### For Windsurf:

1. Get the MCP server path (from Step 2)

2. Direct user to configure Windsurf:
   - Click the "Manage plugins" button in the bottom panel
   - In the plugins list, find "Conduit" (it will show "15 / 15" tools)
   - Click the "Configure" button next to code-understanding or any other server
   - This opens the mcp_config.json file

3. Add Conduit to the mcpServers section:
   ```json
   {
     "mcpServers": {
       "Conduit": {
         "command": "/opt/homebrew/bin/mcp-server-conduit"
       }
     }
   }
   ```
   
   Note: The server name MUST be "Conduit" with a capital C.

4. The configuration file location is:
   - macOS/Linux: `~/.codeium/windsurf/mcp_config.json`
   - Windows: `%USERPROFILE%\.codeium\windsurf\mcp_config.json`

5. After saving, you can verify in the Manage plugins panel that Conduit shows "15 tools"

#### For Other AI Assistants:

If using a different MCP-compatible assistant, the general pattern is:
- Server type: `stdio`
- Command: Full path to `mcp-server-conduit`
- No additional arguments needed

### Step 8: Verify MCP Integration

The easiest way to verify everything is working:

1. **Start a new session** in the AI coding assistant (Claude Code, Claude Desktop, Cursor, Windsurf, etc.)
   - This ensures the MCP tools are properly loaded
   - For Windsurf: You can also click "Refresh" in the Manage plugins panel

2. **Visual verification** (Windsurf only):
   - Open the Manage plugins panel
   - Look for "Conduit 15 / 15" in the list
   - This confirms all 15 Conduit tools are loaded

3. **Simple verification test**:
   Tell the AI assistant: "List all my Atlassian site aliases"
   
   If everything is configured correctly, the AI assistant should:
   - Use the Conduit MCP tool
   - Show your configured site aliases (e.g., "default", "mycompany", etc.)

4. **If the test fails**:
   - Ensure you started a NEW session after adding the MCP server
   - Verify the API token was added to config.yaml
   - Check that the MCP server path is correct
   - See the Troubleshooting section below for detailed help

## Troubleshooting

Help the user troubleshoot any issues they encounter:

### Installation Issues

1. **"Command not found" for mcp-server-conduit**:
   - Ensure PATH is updated (may need terminal restart)
   - For pipx: Run `python -m pipx ensurepath` and restart terminal
   - Try finding the executable manually:
     - macOS/Linux: `find ~/.local -name mcp-server-conduit 2>/dev/null`
     - Windows: Search in `%APPDATA%\Python` or `%LOCALAPPDATA%`

2. **Installation fails**:
   - Check Python version (must be 3.10+)
   - Try different package manager (pipx vs uv vs pip)
   - On Windows, may need to run as administrator
   - Clear pip cache: `pip cache purge`

### MCP Configuration Issues

3. **"List all my Atlassian site aliases" doesn't work**:
   - **Most common**: Forgot to start a NEW session after adding MCP
   - Verify the MCP server path is correct
   - Check for JSON syntax errors in MCP config
   - Try removing and re-adding the MCP server
   - Ensure API token was added to config.yaml

4. **MCP server not found by AI assistant**:
   - Double-check the path from `which`/`where` command
   - On Windows, ensure path uses forward slashes or escaped backslashes
   - Try using the full absolute path
   - Verify file exists at that path

5. **"No Conduit tools available" in AI assistant**:
   - Restart the AI assistant completely
   - Check MCP server name is exactly "Conduit" (capital C) in the configuration
   - For Cursor: Verify in ~/.cursor/mcp.json that the key is "Conduit" not "conduit"
   - For Windsurf: Check ~/.codeium/windsurf/mcp_config.json and verify "Conduit" is capitalized
   - In Windsurf: Check Manage plugins panel - Conduit should show "15 tools"
   - Verify the command path points to `mcp-server-conduit` (not `conduit`)

### Configuration Issues

6. **API token errors**:
   - Ensure no extra spaces before/after token
   - Token should be in quotes in yaml file
   - Verify token hasn't expired
   - Try generating a new token

7. **Site not found errors**:
   - Check site alias matches in config
   - Ensure URL includes https://
   - Verify email matches Atlassian account

### Platform-Specific Issues

8. **Windows-specific**:
   - Use `where` instead of `which` for paths
   - Paths in JSON may need double backslashes: `C:\\\\Users\\\\...`
   - Or use forward slashes: `C:/Users/...`
   - Admin UI has known limitations - this is normal

9. **macOS-specific**:
   - If using Homebrew Python, paths may be in `/opt/homebrew/`
   - Check both `~/.local/bin` and `/opt/homebrew/bin`

10. **Linux-specific**:
    - Ensure `~/.local/bin` is in PATH
    - May need to logout/login for PATH changes

### Verification Steps

If issues persist, help the user verify each component:

1. **Config file exists**: 
   - Linux/macOS: `ls ~/.config/conduit/config.yaml`
   - Windows: `dir %APPDATA%\conduit\config.yaml`

2. **Config has API token**: 
   - Check that `api_token:` has a value (not empty quotes)

3. **MCP server executable exists**:
   - Check the path they're using actually has the file

4. **Try verbose mode in AI assistant**:
   - Some AI assistants show MCP errors in developer/debug mode

## Next Steps

Once the "list all my Atlassian site aliases" command works in the AI assistant:

1. The user can explore MCP capabilities:
   - Search Jira issues: "Search for my open Jira tickets"
   - Get Confluence pages: "Show me pages in the DOCS space"
   - Create issues: "Create a new Jira issue in project ABC"
   - Create Confluence pages: "Create a new Confluence page with markdown"

2. Point them to resources:
   - Conduit documentation: https://github.com/codingthefuturewithai/conduit
   - Report issues: GitHub issues page
   - MCP protocol info: https://modelcontextprotocol.io

## Important Security Reminders

- **NEVER** ask for or handle API tokens
- **ALWAYS** have users add API tokens manually after you complete setup
- **CLEARLY** indicate when they need to add their token
- **REMIND** users to keep their config.yaml file secure

## Summary Checklist

Before considering setup complete, verify:
- [ ] Python 3.10+ is installed
- [ ] Conduit is installed via pipx/uv/pip
- [ ] Configuration file is initialized
- [ ] Atlassian URL and email are configured
- [ ] User has been instructed to add API token manually
- [ ] User has confirmed they added their API token
- [ ] Connection tests pass
- [ ] MCP server path is obtained
- [ ] AI assistant is configured with MCP using `claude mcp add-json` or equivalent
- [ ] New session started and "list all my Atlassian site aliases" test works

## Quick Test After Setup

The simplest verification after everything is configured:
1. Start a NEW session in the AI coding assistant
2. Say: "List all my Atlassian site aliases"
3. If it works, setup is complete!

Remember: Be patient and helpful. Setup can be complex, but once complete, Conduit provides powerful integration between AI assistants and Atlassian tools.