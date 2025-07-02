# Claude Code Slash Commands for Conduit

This directory contains custom slash commands to streamline development workflows for the Conduit project.

## Available Commands

### Core Workflow Commands

#### `/project:start-feature [ISSUE-KEY] [SITE-ALIAS]`
Start work on a new JIRA feature by:
- Fetching the JIRA issue details from the specified Atlassian site
- Creating a feature branch
- Updating JIRA status to "In Progress"
- **Automatically detecting testing approach** (UI vs MCP)
- Creating an implementation plan with appropriate test strategy
- Requesting human review

Example: `/project:start-feature ACT-149 saaga`

#### `/project:test-feature [OPTIONAL-HINTS]`
Intelligently test the current feature by:
- Analyzing the context and changes
- Automatically choosing between UI, API, or MCP testing
- **Intelligently selecting direct vs subprocess execution** based on complexity
- Executing the appropriate test workflow
- No need to specify test type unless you want to override

Example: `/project:test-feature`

#### `/project:test-mcp [TOOL-NAME] [PARAMS]`
Test MCP endpoints using Claude subprocess:
- Launches Claude subprocess with --dangerously-skip-permissions
- Tests with real data from configured sites
- Validates output format and functionality

Example: `/project:test-mcp retrieve_confluence_hierarchy "space_key: ASEP"`

#### `/project:test-api [ENDPOINT-PATTERN] [TEST-TYPE]`
Test backend API endpoints using pytest (direct execution):
- Analyzes API structure and endpoints
- Creates or updates test files
- Runs pytest with appropriate options
- Generates coverage reports
- Supports unit and integration testing
- Best for single endpoints and quick tests

Example: `/project:test-api /api/users all`

#### `/project:test-api-subprocess [TEST-DESCRIPTION]`
Test complex API workflows using Claude subprocess:
- Autonomous test generation and execution
- Multi-service integration testing
- Security and edge case discovery
- Complex authentication flows
- Best for comprehensive API testing

Example: `/project:test-api-subprocess "Order processing with payment gateway"`

#### `/project:test-ui [URL] [TEST-SCENARIO]`
Test UI features using Puppeteer MCP (direct execution):
- Launches browser session for visual testing
- Executes user interaction scenarios
- Takes screenshots for validation
- Supports responsive and accessibility testing
- Best for simple UI checks and quick validations

Example: `/project:test-ui http://localhost:3000 "login flow"`

#### `/project:test-ui-subprocess [TEST-DESCRIPTION]`
Test complex UI flows using Claude subprocess:
- Autonomous test execution with AI agent
- Handles multi-page workflows and edge cases
- Visual validation and exploratory testing
- Cross-browser and responsive testing
- Best for comprehensive E2E scenarios

Example: `/project:test-ui-subprocess "Complete user registration and onboarding"`

#### `/project:complete-feature [SITE-ALIAS]`
Complete the current feature by:
- Running quality checks (linting, tests)
- Committing changes with conventional commits
- Creating a pull request via GitHub CLI
- Updating JIRA issue to "Done" on the specified Atlassian site
- Adding PR link to JIRA

Example: `/project:complete-feature saaga`

#### `/project:post-merge`
Execute post-merge actions:
- Sync local main with remote
- Re-run tests on merged code
- Clean up feature branch
- Update development environment

Example: `/project:post-merge`

### Utility Commands

#### `/project:list-sites`
List all configured Atlassian sites available in Conduit.
- Shows site aliases, URLs, and types
- Use these aliases with commands requiring [SITE-ALIAS]

Example: `/project:list-sites`

#### `/project:workflows/jira-status [ISSUE-KEY] [STATUS] [SITE-ALIAS]`
Quick update of JIRA issue status on the specified Atlassian site.

Example: `/project:workflows/jira-status ACT-149 "Done" saaga`

#### `/project:workflows/run-tests [TEST-TYPE]`
Run project-specific tests:
- `all` - Run all tests and quality checks (default)
- `unit` - Run unit tests only
- `integration` - Run integration tests only
- `mcp` - Run MCP tests only
- `quick` - Fast feedback with fail-fast
- `coverage` - Generate coverage report

Example: `/project:workflows/run-tests quick`

## Usage Tips

1. **Arguments**: Commands accept arguments using `$ARGUMENTS` placeholder
2. **Site Aliases**: Commands that interact with JIRA/Confluence require a site alias parameter
   - Use `mcp__Conduit__list_atlassian_sites` to see available site aliases
   - Examples: 'saaga', 'ctf', or other configured sites
3. **Chaining**: Commands can be used in sequence for complex workflows
4. **Context**: Commands are aware of current directory and git branch

## Important: MCP Tool Preferences for JIRA Operations

**ALWAYS use MCP JIRA tools (not Conduit tools) for the following JIRA operations:**
- Creating JIRA issues: Use `mcp__mcp_jira__create_jira_issue`
- Updating JIRA issues: Use `mcp__mcp_jira__update_jira_issue`
- Searching JIRA issues: Use `mcp__mcp_jira__search_jira_issues`

**Continue using Conduit tools for:**
- Listing Atlassian sites: `mcp__Conduit__list_atlassian_sites`
- JIRA status updates: `mcp__Conduit__update_jira_status`
- Other non-CRUD JIRA operations (boards, sprints, remote links)
- All Confluence operations

## Directory Structure

```
.claude/commands/
├── README.md                 # This file
├── start-feature.md         # Start new feature workflow
├── test-mcp.md             # Test MCP endpoints
├── complete-feature.md      # Complete feature workflow
├── post-merge.md           # Post-merge actions
└── workflows/              # Utility commands
    ├── jira-status.md     # Update JIRA status
    └── run-tests.md       # Run project tests
```

## Adding New Commands

To add a new command:
1. Create a new `.md` file in this directory
2. Add YAML frontmatter with description, usage, and example
3. Write the command implementation using available syntax:
   - `!command` for bash execution
   - `@file` for file references
   - `$ARGUMENTS` for user input
   - MCP tool calls for integrations

## Best Practices

- Keep commands focused on a single workflow
- Include error handling and validation
- Provide clear feedback during execution
- Document expected inputs and outputs
- Test commands before committing

## Intelligent Testing Detection

Claude Code automatically detects the appropriate testing approach:
- **UI Testing**: For frontend changes and user interfaces
- **API Testing**: For backend REST APIs using pytest
- **MCP Testing**: For MCP server tools and integrations

### Direct vs Subprocess Testing

The system intelligently chooses between:
- **Direct Testing**: Quick, deterministic tests for simple scenarios
- **Subprocess Testing**: Comprehensive, exploratory tests for complex flows

Decision factors:
- **Complexity**: Number of steps, interactions, and services
- **Scope**: Single component vs end-to-end workflow
- **Objectives**: Validation vs exploration
- **Test Type**: MCP always uses subprocess

See [Testing Approach Decision Guide](../../workflows/testing-approach-decision-guide.md) for detailed criteria.

## Related Documentation

- [Workflow Documentation](../../workflows/)
- [CLAUDE.md](../../CLAUDE.md) - Project-specific Claude guidance
- [Slash Commands Plan](../../workflows/slash-commands-conversion-plan.md)
- [Testing Approach Comparison](../../workflows/testing-approach-comparison.md)