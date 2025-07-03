# Conduit MCP Server Development Memory

## Latest Status (2025-07-03)

### Successfully Completed Features
1. **ACT-150**: Confluence attachment support via MCP - DONE
   - Added ability to attach and embed images in Confluence pages
   - Both create and update tools support attachments
   - Simplified API to accept pure markdown with automatic image conversion
   - Tool descriptions updated to show markdown image syntax to MCP clients

2. **Version Upgrade**: Successfully upgraded from 0.1.12 to 0.1.15
   - Installation method: homebrew's pip (`/opt/homebrew/bin/pip3`)
   - Upgraded using: `pip3 uninstall conduit-connect` then `pip3 install conduit-connect==0.1.15`
   - Confirmed working via sub-agent testing

### Key Technical Improvements
1. **Markdown Image Support**
   - Added `convert_markdown_images_to_storage()` function in services.py
   - Converts `![alt](filename.png)` to Confluence storage format automatically
   - Only converts images that are being attached, leaves external images as markdown

2. **MCP Tool Naming**
   - Renamed `update_confluence_page` to `update_confluence_page_from_markdown` for clarity
   - Both create and update tools now explicitly indicate markdown input in their names

3. **MCP Tool Descriptions**
   - Fixed critical issue: MCP clients only see tool descriptions, not Python docstrings
   - Added image embed syntax directly to tool descriptions
   - Example: "Can attach and embed images - use standard markdown syntax: ![alt text](filename.png)"

### Testing Results
Successfully tested with sub-agent on 2025-07-03:
- Created page "MCP Tool Test - Image Embedding Demo" in ACT space
- Attached and embedded mcp-architecture.png during creation
- Updated page with mcp-flow.png using update tool
- Both images properly embedded using markdown syntax
- Page URL: https://codingthefuturewithai.atlassian.net/wiki/spaces/ACT/pages/81592321

### Open Issues
- **ACT-221**: Add ability to download attachments during page retrieval (created, assigned to timkitch@codingthefuture.ai, in Sprint 6)

### Installation Notes
- Package name: conduit-connect
- PyPI: https://pypi.org/project/conduit-connect/
- Binary: mcp-server-conduit (installed at /opt/homebrew/bin/)
- Development location: /Users/timkitchens/projects/ai-projects/conduit