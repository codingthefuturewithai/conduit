# Command Updates Log

## 2025-07-02: Major Workflow Enhancement

### Commands Modified

#### Core Workflow Commands

1. **start-feature.md**
   - Added: Site alias parameter support
   - Added: Workflow hints showing next steps
   - Changed: Usage from `[ISSUE-KEY]` to `[ISSUE-KEY] [SITE-ALIAS]`
   - Added: Tips to save site alias for later use

2. **test-feature.md**
   - Added: Intelligent detection for UI/API/MCP testing
   - Added: Direct vs subprocess decision logic
   - Added: Workflow hints for next steps
   - Added: Troubleshooting guidance

3. **complete-feature.md**
   - Added: Site alias parameter support
   - Added: Workflow hints for post-PR steps
   - Changed: Usage from no args to `[SITE-ALIAS]`
   - Added: Automatic JIRA issue key extraction from branch

4. **post-merge.md**
   - Added: Workflow hints for starting next feature
   - Added: Reference to list-sites command
   - Added: Team collaboration suggestions

#### Utility Commands

5. **workflows/jira-status.md**
   - Added: Site alias parameter support
   - Changed: Usage from `[ISSUE-KEY] [STATUS]` to `[ISSUE-KEY] [STATUS] [SITE-ALIAS]`
   - Added: Argument parsing section

### Commands Created

1. **test-ui-subprocess.md**
   - Purpose: Complex UI flow testing with Claude subprocess
   - Features: Autonomous exploration, visual validation
   - Usage: `/project:test-ui-subprocess [TEST-DESCRIPTION]`

2. **test-api-subprocess.md**
   - Purpose: Comprehensive API testing with Claude subprocess
   - Features: Security testing, integration testing, edge case discovery
   - Usage: `/project:test-api-subprocess [TEST-DESCRIPTION]`

3. **list-sites.md**
   - Purpose: List all configured Atlassian sites
   - Features: Shows aliases, URLs, and types
   - Usage: `/project:list-sites`

### Documentation Updates

1. **commands/README.md**
   - Updated all command descriptions with new parameters
   - Added subprocess testing commands
   - Added section on intelligent testing detection
   - Added site alias usage tips
   - Updated examples with site aliases

2. **workflows/CLAUDE.md**
   - Added subprocess testing to integration points
   - Updated workflow list with new testing approaches
   - Added testing approach selection guidance

3. **CLAUDE.md (root)**
   - Added comprehensive testing approaches section
   - Added subprocess testing examples
   - Added decision criteria for test selection

### Key Changes Summary

#### Before
- Commands assumed single Atlassian site ("saaga")
- Testing was type-specific with manual selection
- No guidance between workflow steps
- Limited to direct testing approaches

#### After
- Full multi-site support with explicit aliases
- Intelligent test detection and approach selection
- Complete workflow guidance with next steps
- Both direct and subprocess testing options

### Implementation Notes

1. **Backward Compatibility**
   - Commands now require site alias (breaking change)
   - Users must specify site for JIRA operations
   - Test commands maintain compatibility

2. **User Experience**
   - Clear hints guide workflow progression
   - Reduced cognitive load with suggestions
   - Self-documenting command structure

3. **Technical Patterns**
   - `$ARGUMENTS` parsing for multiple parameters
   - Consistent "Next Steps" sections
   - Subprocess invocation patterns established

### Rollout Considerations

1. **User Communication**
   - Notify team about site alias requirement
   - Share list-sites command for discovery
   - Explain new testing capabilities

2. **Migration Path**
   - Update any scripts using old command syntax
   - Document site aliases for each team
   - Create team-specific guides if needed

### Validation Checklist

- [x] All JIRA commands support site alias
- [x] Test commands have intelligent detection
- [x] Workflow hints guide users
- [x] Documentation is updated
- [x] New commands are created
- [x] Examples use new syntax

### Next Iteration Ideas

1. **State Persistence**
   - Save site alias in branch metadata
   - Remember test preferences
   - Track workflow progress

2. **Team Defaults**
   - Per-project site configurations
   - Team-specific test preferences
   - Shared workflow templates

3. **Advanced Integration**
   - Slack notifications at steps
   - Automatic PR assignments
   - JIRA board visualization