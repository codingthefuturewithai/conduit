# Workflow: Starting a New Feature

## Overview
This workflow describes how to begin work on a new feature from a JIRA issue, including retrieving the issue, creating a feature branch, updating status, and planning the implementation.

## Prerequisites
- JIRA access with appropriate permissions
- Git repository cloned locally
- Conduit MCP server configured
- Context7 MCP server configured (for framework/library documentation)

## Steps

### 1. Select Atlassian Site
```bash
# List available Atlassian sites
claude -p "Use mcp__Conduit__list_atlassian_sites to show all configured sites"

# Select the appropriate site for your work
# Default site alias is 'saaga'
```

### 2. Retrieve and Analyze the JIRA Issue
```bash
# Fetch the issue details using Conduit
claude -p "Use mcp__Conduit__search_jira_issues to search for key = [ISSUE-KEY] with site_alias:[SITE]"

# Review the issue details, acceptance criteria, and requirements
```

### 3. Create Feature Branch
```bash
# Create a new feature branch following the naming convention
git checkout -b feature/[ISSUE-KEY]-[brief-description]

# Example: git checkout -b feature/ACT-149-confluence-hierarchical-retrieval
```

### 4. Update JIRA Status to "In Progress"
```bash
# Update the issue status using Conduit MCP tool
claude -p "Use mcp__Conduit__update_jira_status to update [ISSUE-KEY] to 'In Progress' status using site_alias:[SITE]"
```

### 5. Research Technical Requirements (if needed)
```bash
# Use Context7 for framework/library documentation
claude -p "Use mcp__context7__resolve-library-id to find documentation for [LIBRARY_NAME]"
claude -p "Use mcp__context7__get-library-docs with the resolved library ID to get specific documentation"
```

### 6. Create Implementation Plan
- Review acceptance criteria thoroughly
- Identify all required components and changes
- Determine implementation order
- Consider testing requirements
- Document any risks or dependencies
- Research any unfamiliar frameworks or libraries using Context7

### 7. Human Review of Plan
Present your implementation plan for review:
```
## Implementation Plan for [ISSUE-KEY]

### Overview
[Brief description of the approach]

### Components to Modify/Create
1. [Component A]: [Description of changes]
2. [Component B]: [Description of changes]

### Implementation Order
1. [First task]
2. [Second task]
3. [Testing]
4. [Documentation]

### Testing Strategy
- [Test approach]

### Risks/Dependencies
- [Any identified risks]

**Please review this plan before proceeding. Type 'approved' to continue or provide feedback.**
```

### 8. Use exit_plan_mode After Approval
Once the plan is approved by human review:
```
exit_plan_mode(plan="[Your approved implementation plan]")
```

### 9. Commit Frequently During Implementation
Make frequent commits as you complete each part of the implementation:
```bash
# After implementing a component and tests pass
git add [modified files]
git commit -m "feat: Implement [component name]

- [What was implemented]
- [Tests added/passing]"

# Example workflow:
# 1. Implement Component A
# 2. Run tests for Component A
# 3. If tests pass → git commit
# 4. Move to Component B
# 5. Repeat

# This ensures you can always revert to a known good state
```

## Best Practices
- Always work on a feature branch, never directly on main
- Ensure the JIRA issue has clear acceptance criteria before starting
- Keep branch names consistent with team conventions
- Update JIRA status promptly to reflect actual progress
- Get human approval for the plan before implementation
- Use Context7 to research unfamiliar technologies
- **Commit frequently** - After each successful component implementation and test
- Use descriptive commit messages that reference what was completed

## Default Configuration
- **Default site alias**: `saaga`
- Always check available sites first if unsure
- Use Conduit for all JIRA and Confluence operations