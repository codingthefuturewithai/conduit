# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MCP Tool Preferences

When working with JIRA operations, ALWAYS use the following tool preferences:

**Use MCP JIRA tools for:**
- Creating JIRA issues: `mcp__mcp_jira__create_jira_issue`
- Updating JIRA issues: `mcp__mcp_jira__update_jira_issue`  
- Searching JIRA issues: `mcp__mcp_jira__search_jira_issues`

**Use Conduit tools for:**
- Listing Atlassian sites: `mcp__Conduit__list_atlassian_sites`
- JIRA status updates: `mcp__Conduit__update_jira_status`
- Other JIRA operations (boards, sprints, remote links)
- All Confluence operations

## Build/Test/Lint Commands

- Install dev dependencies: `pip install -e ".[dev]"`
- Run all tests: `pytest`
- Run single test: `pytest tests/path/to/test_file.py::test_function_name`
- Run tests with coverage: `pytest --cov=conduit`
- Format code: `black .`
- Sort imports: `isort .`
- Type checking: `mypy .`
- Lint code: `ruff .`

## Testing Approaches

### Direct Testing (Default)
Use for quick, deterministic tests:
- Unit tests: `pytest tests/unit/`
- Single endpoints: `pytest tests/integration/test_specific_endpoint.py`
- Component checks: Use Puppeteer MCP directly for simple UI validation

### Subprocess Testing
Use Claude subprocess for complex scenarios:
- **MCP Tools**: Always use subprocess with `claude -p "[PROMPT]" --dangerously-skip-permissions`
- **Complex UI Flows**: Multi-page workflows, visual validation, exploratory testing
- **API Integrations**: Multi-service workflows, security testing, edge case discovery

Example subprocess commands:
```bash
# MCP Testing
claude -p "Test the retrieve_confluence_hierarchy tool with space_key ASEP" --dangerously-skip-permissions

# Complex UI Testing
claude -p "Test complete e-commerce checkout flow including cart, payment, and confirmation" --dangerously-skip-permissions

# API Integration Testing
claude -p "Test order API with payment gateway integration, including error scenarios" --dangerously-skip-permissions
```

### Decision Criteria
Choose subprocess testing when:
- Testing involves >5 sequential steps
- Need visual validation or exploratory testing
- Testing cross-service integrations
- Natural language test specs in JIRA
- MCP tool testing (always)

## Code Style Guidelines

- **Imports**: Standard library first, third-party second, local imports last. Use `isort`.
- **Formatting**: Follow Black formatting standards.
- **Type Annotations**: Use type hints for all function parameters and return values.
- **Naming**: Classes use CamelCase, functions/variables use snake_case, constants use UPPER_SNAKE_CASE.
- **Documentation**: Google-style docstrings for classes and functions.
- **Error Handling**: Use custom exceptions from `conduit.core.exceptions`. Include informative error messages.
- **Logging**: Use the configured logger from `conduit.core.logger`.
- **Testing**: Write pytest tests for new functionality, including both happy paths and error cases.