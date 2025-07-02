# Workflow: Testing MCP Endpoints with Claude Subprocess

## Overview
This workflow describes how to use Claude as a subprocess to test MCP server endpoints with real data, providing end-to-end validation of new functionality.

## Prerequisites
- MCP server must be installed and available
- Claude CLI must be installed
- The MCP tool you're implementing/testing must be:
  - Fully implemented in the codebase
  - Registered with the MCP server (via `@mcp_server.tool` decorator)
  - Installed in development mode (`pip install -e ".[dev]"`)

## Steps

### 1. Identify the MCP Tool to Test
Determine the exact tool name from your implementation:
- Check `@mcp_server.tool` decorators in the code
- Tool names typically follow pattern: `mcp__[ServerName]__[tool_name]`

### 2. Prepare Test Scenarios
Based on acceptance criteria, identify:
- Required parameters
- Expected data sources (site aliases, spaces, projects)
- Edge cases to validate

### 3. Launch Claude Subprocess for Testing
```bash
# Basic syntax
claude -p "[PROMPT_WITH_MCP_INSTRUCTIONS]" --dangerously-skip-permissions

# Full example
claude -p "Use the [MCP_TOOL_NAME] MCP tool to [SPECIFIC_ACTION]. Use these parameters: [PARAMS]. Use the '[SITE_ALIAS]' site alias." --dangerously-skip-permissions
```

### 4. Validate Results
Check that the output:
- Contains expected data structure
- Handles parameters correctly
- Returns appropriate metadata
- Formats output as specified

## Examples

### Testing a Hierarchical Retrieval Tool
```bash
claude -p "Use the retrieve_confluence_hierarchy MCP tool to get the page hierarchy for the ASEP space in Confluence. Start from the space root and use a batch_size of 10. Use the 'saaga' site alias." --dangerously-skip-permissions
```

### Testing with Specific Starting Point
```bash
claude -p "Use the retrieve_confluence_hierarchy MCP tool to get the page hierarchy for the DOCS space. Search for the page titled 'API Reference' and use its ID as the parent_page_id parameter. Use a batch_size of 20. Use the 'ctf' site alias." --dangerously-skip-permissions
```

### Testing Search Functionality
```bash
claude -p "Use the search_issues MCP tool to find all issues in project PROJ with status 'In Progress'. Use the 'default' site alias." --dangerously-skip-permissions
```

## Advanced Testing

### Testing Multiple Scenarios
Create a sequence of tests to validate different aspects:
1. Test with minimal parameters (defaults)
2. Test with all parameters specified
3. Test edge cases (empty results, large datasets)
4. Test error handling (invalid parameters)

### Capturing Detailed Output
For debugging or documentation:
```bash
# Redirect output to file
claude -p "[TEST_PROMPT]" --dangerously-skip-permissions > test_results.md

# With timestamp
claude -p "[TEST_PROMPT]" --dangerously-skip-permissions > "test_$(date +%Y%m%d_%H%M%S).md"
```

## Best Practices
- Always use `--dangerously-skip-permissions` for automated testing
- Test with real data when possible for true validation
- Include parameter variations in test scenarios
- Document unexpected behaviors or limitations discovered
- Save test outputs for future reference

## Troubleshooting
- If tool not found: Check MCP server is running and tool name is correct
- If authentication fails: Verify site_alias and credentials
- If no data returned: Check permissions and data existence
- Use verbose prompts to get detailed output formatting