# CLAUDE.md - Workflows Directory

This file provides guidance to Claude Code when working with workflows in this directory.

## Directory Overview

This directory contains SDLC (Software Development Lifecycle) workflow documentation for AI-assisted development. These workflows standardize how development tasks are approached and completed.

## Current Workflows

### Feature Development Workflows (Already Implemented)
1. **01-start-feature-workflow.md** - How to begin work on a new feature from a JIRA issue
2. **02-test-mcp-with-claude-subprocess.md** - Testing MCP endpoints using Claude subprocess
3. **02-test-backend-api-with-pytest.md** - Testing backend APIs using pytest
4. **02-test-ui-with-puppeteer-mcp.md** - Testing UI features using Puppeteer MCP server
5. **03-complete-feature-workflow.md** - Completing features with commits, PRs, and JIRA updates
6. **04-post-merge-workflow.md** - Actions to take after PR is merged

### SDLC Workflows Documentation
- **sdlc-workflows-for-asep-10.md** - Comprehensive list of 15 additional SDLC workflows identified for ASEP-10
- **testing-approach-comparison.md** - Guide for choosing between MCP, API, and UI testing approaches
- **testing-approach-decision-guide.md** - Decision guide for direct vs subprocess testing

## Workflow Standards

### Naming Convention
- Use numbered prefixes for sequential workflows (01-, 02-, etc.)
- Use descriptive names with hyphens between words
- End with `-workflow.md`

### Workflow Structure
Each workflow should include:
1. **Overview** - Brief description of the workflow's purpose
2. **Prerequisites** - What needs to be in place before starting
3. **Steps** - Numbered, actionable steps with examples
4. **Best Practices** - Tips for successful execution
5. **Troubleshooting** - Common issues and solutions

### Code Examples
- Use bash code blocks for commands
- Include actual tool names and parameters
- Provide real examples with placeholder values in brackets

### Integration Points
- **JIRA**: Use mcp__Conduit tools for issue management
- **Confluence**: Use mcp__Conduit tools for documentation
- **Git/GitHub**: Use standard git commands and gh CLI
- **Claude subprocess**: Use for testing MCP tools with --dangerously-skip-permissions
- **Subprocess Testing**: Use for complex UI flows, API integrations, and exploratory testing

## Usage Guidelines

### For New Workflows
1. Follow the existing workflow structure
2. Include specific MCP tool names when applicable
3. Add troubleshooting sections based on real issues encountered
4. Test the workflow before documenting

### For Updates
1. Maintain backward compatibility
2. Document what changed and why
3. Update related workflows if affected
4. Test the updated workflow end-to-end

## Key Principles
- **Clarity**: Steps should be unambiguous and actionable
- **Completeness**: Cover the entire process from start to finish
- **Consistency**: Use similar structure and terminology across workflows
- **Practicality**: Include real examples and common scenarios
- **Maintainability**: Keep workflows up-to-date with tool changes

## Related JIRA Issues
- **ACT-149**: Confluence hierarchical retrieval (used as example in workflows)
- **ASEP-10**: SDLC documentation initiative that spawned these workflows

## Testing Workflows
When testing a workflow:
1. Follow it step-by-step as written
2. Note any ambiguities or missing steps
3. Verify all commands work as expected
4. Update based on findings

### Testing Approach Selection
When workflows involve testing:
1. **Simple/Quick Tests**: Use direct testing for fast feedback
2. **Complex/Exploratory**: Use subprocess testing for comprehensive coverage
3. **MCP Tools**: Always use subprocess testing
4. **Decision Factors**: Complexity, scope, objectives, and test type

See the **testing-approach-decision-guide.md** for detailed criteria.

## Future Enhancements
- Add mermaid diagrams to visualize workflow steps
- Create workflow templates for common patterns
- Build automation tools to execute workflow steps
- Add metrics to track workflow effectiveness