# Plan for Converting Workflows to Claude Code Slash Commands

## Overview
This document outlines the plan for converting our SDLC workflows into Claude Code slash commands for improved efficiency and consistency.

## 1. Command Structure Design

### Project-level commands (in `.claude/commands/`)
- `/project:start-feature [ISSUE-KEY]` - Start new feature development
- `/project:test-mcp [TOOL-NAME]` - Test MCP endpoints
- `/project:complete-feature` - Complete feature with PR creation
- `/project:post-merge` - Execute post-merge actions

### Workflow-specific commands
- `/project:jira-status [ISSUE-KEY] [STATUS]` - Update JIRA status
- `/project:create-pr [TITLE]` - Create GitHub PR with template
- `/project:run-tests` - Run project-specific tests

## 2. Implementation Approach

### Phase 1: Core Feature Development Commands
```
.claude/commands/
├── start-feature.md
├── test-mcp.md
├── complete-feature.md
└── post-merge.md
```

### Phase 2: Utility Commands
```
.claude/commands/
├── workflows/
│   ├── jira-status.md
│   ├── create-pr.md
│   └── run-tests.md
└── sdlc/
    ├── bug-fix.md
    ├── hotfix.md
    └── release.md
```

## 3. Command Features to Leverage

- **Arguments**: Use `$ARGUMENTS` for dynamic values (ISSUE-KEY, etc.)
- **Bash execution**: Use `!` prefix for git commands
- **File references**: Use `@` for including workflow templates
- **Context awareness**: Commands can reference current branch, working directory

## 4. Example Command Implementations

### start-feature.md
```markdown
---
description: Start work on a new JIRA feature
usage: /project:start-feature [ISSUE-KEY]
---

Fetch JIRA issue $ARGUMENTS from the 'saaga' site and create a feature branch.

!git checkout -b feature/$ARGUMENTS-description

Use mcp__Conduit__search_jira_issues to fetch issue $ARGUMENTS.
Update status to "In Progress" using mcp__Conduit__update_jira_status.
Create implementation plan based on acceptance criteria.
```

### test-mcp.md
```markdown
---
description: Test MCP tool with Claude subprocess
usage: /project:test-mcp [TOOL-NAME] [PARAMS]
---

Launch Claude subprocess to test the $ARGUMENTS MCP tool:

!claude -p "Use the $ARGUMENTS MCP tool with the following parameters..." --dangerously-skip-permissions
```

## 5. Advanced Features to Include

- **Chained commands**: Commands that trigger other commands
- **Conditional logic**: Different paths based on project type
- **Templates**: Reusable snippets for common patterns
- **Validation**: Check prerequisites before executing

## 6. Benefits of Slash Command Approach

1. **Speed**: Single command instead of multi-step process
2. **Consistency**: Standardized execution across team
3. **Discoverability**: Easy to list and find commands
4. **Maintainability**: Update workflow in one place
5. **Composability**: Chain commands for complex workflows

## 7. Migration Strategy

### Pilot Phase
- Convert start-feature workflow first
- Test with small group
- Gather feedback

### Expansion Phase
- Convert remaining core workflows
- Add utility commands
- Document best practices

### Optimization Phase
- Add advanced features
- Create command aliases
- Build command library

## 8. Considerations

- **Error handling**: Commands should validate inputs
- **Help text**: Include clear usage examples
- **Defaults**: Smart defaults for common scenarios
- **Integration**: Ensure MCP tools work within commands
- **Security**: No sensitive data in command files

## 9. Success Metrics

- Reduced time to start features (target: 50% reduction)
- Increased workflow compliance (target: 90%+)
- Developer satisfaction scores
- Fewer workflow-related questions

## 10. Next Steps

1. Create `.claude/commands/` directory structure
2. Implement pilot start-feature command
3. Test with real JIRA issues
4. Document lessons learned
5. Expand to other workflows

## Implementation Timeline

- Week 1: Set up directory structure and pilot command
- Week 2: Test and refine pilot command
- Week 3-4: Convert remaining core workflows
- Week 5-6: Add utility commands and documentation
- Week 7-8: Rollout and training