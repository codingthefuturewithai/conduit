# Workflow: Starting a New Feature

## Overview
This workflow describes how to begin work on a new feature from a JIRA issue, including retrieving the issue, creating a feature branch, updating status, and planning the implementation.

## Prerequisites
- JIRA access with appropriate permissions
- Git repository cloned locally
- MCP tools configured (mcp_jira and Conduit)

## Steps

### 1. Retrieve and Analyze the JIRA Issue
```bash
# Fetch the issue details using MCP JIRA tool
claude -p "Use the mcp__mcp_jira__search_jira_issues tool to fetch [ISSUE-KEY] from the [PROJECT] project"

# Or use Conduit's search (if you need more features)
claude -p "Use mcp__Conduit__search_jira_issues to search for key = [ISSUE-KEY] with site_alias:[SITE]"
```

### 2. Create Feature Branch
```bash
# Create a new feature branch following the naming convention
git checkout -b feature/[ISSUE-KEY]-[brief-description]

# Example: git checkout -b feature/ACT-149-confluence-hierarchical-retrieval
```

### 3. Update JIRA Status to "In Progress"
```bash
# Update the issue status using Conduit MCP tool
claude -p "Use mcp__Conduit__update_jira_status to update [ISSUE-KEY] to 'In Progress' status using site_alias:[SITE]"

# Or directly if you have the tool available:
mcp__Conduit__update_jira_status key:[ISSUE-KEY] status:"In Progress" site_alias:[SITE]
```

### 4. Create Implementation Plan
- Review acceptance criteria thoroughly
- Identify all required components and changes
- Determine implementation order
- Consider testing requirements
- Document any risks or dependencies

### 5. Use exit_plan_mode to Begin Implementation
When ready to start coding, use the exit_plan_mode tool:
```
exit_plan_mode(plan="
1. Component A: Description of changes
2. Component B: Description of changes
3. Tests: Description of test coverage
4. Documentation: Updates needed
")
```

## Best Practices
- Always work on a feature branch, never directly on main
- Ensure the JIRA issue has clear acceptance criteria before starting
- Keep branch names consistent with team conventions
- Update JIRA status promptly to reflect actual progress
- Create a clear plan before writing code

## Common Site Aliases
- `ctf` - CodingTheFuture instance
- `saaga` - Saaga team instance
- Check available sites with: `mcp__Conduit__list_atlassian_sites`