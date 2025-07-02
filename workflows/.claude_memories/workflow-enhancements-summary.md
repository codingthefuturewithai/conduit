# Workflow Enhancements Summary

## Overview
This document captures the significant enhancements made to the Conduit project's workflow system, including subprocess testing integration, site alias support, and workflow guidance improvements.

## Key Enhancements

### 1. Subprocess Testing Integration
**Date**: 2025-07-02

#### What Changed
- Extended testing capabilities beyond MCP to include UI and API subprocess testing
- Created intelligent test selection in `/project:test-feature` command
- Added decision criteria for choosing between direct and subprocess testing

#### New Commands
- `/project:test-ui-subprocess` - For complex UI flows
- `/project:test-api-subprocess` - For comprehensive API testing

#### Decision Framework
- **Direct Testing**: Quick, deterministic tests (unit tests, single endpoints, simple UI checks)
- **Subprocess Testing**: Complex workflows, exploratory testing, visual validation, security testing
- **MCP Testing**: Always uses subprocess (unchanged)

### 2. Site Alias Support
**Date**: 2025-07-02

#### What Changed
- Updated all JIRA/Confluence-related commands to require site alias parameter
- Removed hardcoded "saaga" references
- Added support for multiple Atlassian account configurations

#### Updated Commands
- `/project:start-feature [ISSUE-KEY] [SITE-ALIAS]`
- `/project:complete-feature [SITE-ALIAS]`
- `/project:workflows/jira-status [ISSUE-KEY] [STATUS] [SITE-ALIAS]`

#### New Command
- `/project:list-sites` - Lists all configured Atlassian sites

### 3. Workflow Guidance System
**Date**: 2025-07-02

#### What Changed
- Added "Next Steps" sections to all workflow commands
- Implemented workflow hints to guide users through the development process
- Created self-documenting command flow

#### Enhanced Commands
All core workflow commands now include:
- Clear next steps after completion
- Command examples with proper syntax
- Tips for troubleshooting
- Links to related commands

## Technical Implementation Details

### Testing Approach Detection
The `/project:test-feature` command now uses these indicators:

**UI Testing Indicators**:
- Changes in: src/components/, src/pages/, src/views/, app/, frontend/
- File extensions: .jsx, .tsx, .vue, .svelte
- JIRA mentions: UI, interface, button, form, page, screen

**API Testing Indicators**:
- Changes in: api/, backend/, routers/, endpoints/, controllers/
- File extensions: .py with decorators (@app.route, @router, @api_view)
- JIRA mentions: API, endpoint, REST, HTTP, validation

**MCP Testing Indicators**:
- Changes in: mcp/, tools/
- @mcp_server decorators
- MCP server configuration files

### Subprocess Testing Criteria
Choose subprocess when:
- Testing involves >5 sequential steps
- Need visual validation or exploratory testing
- Testing cross-service integrations
- Natural language test specs in JIRA
- MCP tool testing (always)

## Documentation Updates

### New Documents Created
1. **testing-approach-decision-guide.md** - Comprehensive guide for choosing testing approaches
2. **test-ui-subprocess.md** - Command for UI subprocess testing
3. **test-api-subprocess.md** - Command for API subprocess testing
4. **list-sites.md** - Command to list Atlassian sites

### Updated Documents
1. **CLAUDE.md** - Added testing approaches section with subprocess examples
2. **workflows/CLAUDE.md** - Added subprocess testing guidance
3. **commands/README.md** - Updated with new commands and site alias requirements
4. All existing command files - Added workflow hints and site alias support

## Usage Patterns

### Complete Feature Development Flow
```bash
# 1. Start feature with site alias
/project:start-feature ACT-123 saaga

# 2. Implement feature (manual coding)

# 3. Test (automatically detects approach)
/project:test-feature

# 4. Complete with site alias
/project:complete-feature saaga

# 5. Post-merge cleanup
/project:post-merge
```

### Testing Decision Flow
```
/project:test-feature
├── Detects test type (UI/API/MCP)
├── Evaluates complexity
└── Chooses approach
    ├── Direct: Quick validation
    └── Subprocess: Comprehensive testing
```

## Best Practices Established

### For Site Aliases
- Always check available sites with `/project:list-sites`
- Store site alias for use throughout feature workflow
- Use consistent site alias for related operations

### For Testing
- Let `/project:test-feature` intelligently choose approach
- Use subprocess for exploratory testing
- Use direct for CI/CD and quick checks
- Always use subprocess for MCP testing

### For Workflow Navigation
- Follow the hints provided after each command
- Use the suggested next command
- Complete the full workflow cycle

## Future Considerations

### Potential Enhancements
1. **Workflow State Persistence** - Save site alias and issue key between commands
2. **Interactive Workflows** - Single command that guides through all steps
3. **Automated Command Chaining** - Option to auto-execute next steps
4. **Team Configurations** - Project-specific default site aliases

### Monitoring Points
- User adoption of subprocess testing
- Frequency of site alias errors
- Workflow completion rates
- Command usage patterns

## Impact Summary

These enhancements provide:
1. **Better Testing Coverage** - Subprocess testing finds more issues
2. **Multi-Site Support** - Work with multiple Atlassian instances
3. **Improved Developer Experience** - Clear guidance throughout workflow
4. **Flexibility** - Choose testing approach based on needs
5. **Self-Documentation** - Commands guide their own usage

The workflow system is now more robust, flexible, and user-friendly, supporting both simple and complex development scenarios.