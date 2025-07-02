# SDLC Workflows for ASEP-10

## Overview
This document captures all SDLC workflows identified for addressing ASEP-10: "Create comprehensive documentation of our SDLC structure, artifacts, and practices for AI-assisted development".

## Existing Feature Development Workflows
These workflows have already been created and uploaded to Confluence:

### 1. Starting a New Feature (01-start-feature-workflow.md)
- Select Atlassian site
- Retrieve and analyze JIRA issue
- Create feature branch
- Update JIRA status to "In Progress"
- Research technical requirements using Context7
- Create implementation plan
- Human review of plan
- Use exit_plan_mode after approval
- Commit frequently during implementation

### 2. Testing MCP Endpoints with Claude Subprocess (02-test-mcp-with-claude-subprocess.md)
- Identify MCP tool to test
- Prepare test scenarios
- Launch Claude subprocess with --dangerously-skip-permissions
- Validate results
- Document test outcomes

### 3. Completing a Feature (03-complete-feature-workflow.md)
- Stage and commit changes with conventional commits
- Push feature branch
- Create pull request using GitHub CLI
- Update JIRA issue to Done
- Add PR link to JIRA

### 4. Post-Merge Actions (04-post-merge-workflow.md)
- Sync local repository with remote main
- Re-run feature tests on merged code
- Run project-specific quality checks
- Clean up feature branch
- Update local development environment
- Document any post-merge issues

## Additional SDLC Workflows to Create

### Project-Level Workflows

#### 1. Project Initiation Workflow
**Purpose**: Standardize how new projects are set up
- Create project structure and repositories
- Set up CI/CD pipelines
- Configure development environments
- Create initial JIRA project and epics
- Set up Confluence space with standard templates
- Initialize README, CONTRIBUTING, and LICENSE files
- Configure branch protection rules

#### 2. Requirements Gathering Workflow
**Purpose**: Ensure comprehensive capture of requirements
- Stakeholder interview process
- Requirements documentation in Confluence
- Create user stories in JIRA
- Acceptance criteria definition
- Technical feasibility assessment
- Priority and dependency mapping
- Review and approval process

#### 3. Architecture Design Workflow
**Purpose**: Document architectural decisions
- Create architecture decision records (ADRs)
- Design system components and interactions
- Document in Confluence with diagrams
- Technical review process
- Update project documentation
- Create implementation epics

### Sprint & Planning Workflows

#### 4. Sprint Planning Workflow
**Purpose**: Consistent sprint preparation
- Review backlog and priorities
- Story point estimation
- Capacity planning
- Sprint goal definition
- Task breakdown and assignment
- Update sprint board in JIRA
- Document sprint plan in Confluence

#### 5. Daily Standup Workflow
**Purpose**: Effective daily coordination
- Update JIRA tasks before standup
- Report blockers and dependencies
- Document key decisions
- Update sprint burndown
- Schedule follow-up discussions

#### 6. Sprint Review & Retrospective Workflow
**Purpose**: Continuous improvement
- Demo completed features
- Gather stakeholder feedback
- Update documentation
- Conduct retrospective
- Create improvement action items
- Update velocity metrics

### Development Workflows

#### 7. Bug Fix Workflow
**Purpose**: Systematic bug resolution
- Reproduce and document bug
- Create bug ticket in JIRA
- Root cause analysis
- Implement fix with tests
- Regression testing
- Update documentation
- Deploy fix following release process

#### 8. Hotfix/Emergency Release Workflow
**Purpose**: Handle critical production issues
- Assess severity and impact
- Create hotfix branch from production
- Implement minimal fix
- Emergency testing protocol
- Fast-track review process
- Production deployment
- Post-mortem documentation

#### 9. Code Review Workflow
**Purpose**: Maintain code quality
- Self-review checklist
- Create PR with detailed description
- Assign appropriate reviewers
- Address review feedback
- Ensure CI/CD passes
- Approval and merge process
- Update related documentation

#### 10. Technical Debt Management Workflow
**Purpose**: Track and address technical debt
- Identify and document debt items
- Create technical debt tickets
- Prioritize based on impact
- Schedule debt reduction sprints
- Track debt metrics
- Report progress to stakeholders

### Release & Deployment Workflows

#### 11. Release Planning Workflow
**Purpose**: Coordinate releases
- Define release scope
- Create release branch
- Feature freeze process
- Release testing protocol
- Documentation updates
- Stakeholder communication
- Go/no-go decision process

#### 12. Deployment Workflow
**Purpose**: Consistent deployment process
- Pre-deployment checklist
- Database migration handling
- Environment-specific configurations
- Deployment execution
- Smoke testing
- Rollback procedures
- Post-deployment verification

#### 13. Post-Release Monitoring Workflow
**Purpose**: Ensure release stability
- Monitor system metrics
- Check error rates and logs
- User feedback collection
- Performance analysis
- Create follow-up tickets
- Update release notes
- Schedule retrospective

### Support & Maintenance Workflows

#### 14. Production Incident Response Workflow
**Purpose**: Handle production issues
- Incident detection and alerting
- Severity assessment
- Incident commander assignment
- Communication protocols
- Resolution tracking
- Post-incident review
- Documentation and learning

#### 15. Documentation Update Workflow
**Purpose**: Keep documentation current
- Identify documentation gaps
- Create documentation tasks
- Write/update documentation
- Technical review process
- Publish to appropriate channels
- Notify relevant teams
- Archive outdated content

## Implementation Recommendations

### Phase 1: Core Development Workflows
- Focus on workflows 1-10 as they cover the primary development cycle
- These directly support day-to-day development activities

### Phase 2: Release & Operations Workflows
- Implement workflows 11-15 for mature release management
- These ensure smooth deployments and operations

### Integration Points
- All workflows should integrate with JIRA for tracking
- Use Confluence for persistent documentation
- Leverage MCP tools for automation where possible
- Include AI assistance checkpoints for efficiency

### Success Metrics
- Reduced time to complete standard tasks
- Increased consistency across teams
- Better documentation coverage
- Fewer production incidents
- Improved developer satisfaction

## Next Steps
1. Review and prioritize workflows with the team
2. Create detailed templates for each workflow
3. Pilot workflows with a single team
4. Gather feedback and iterate
5. Roll out across all teams
6. Establish continuous improvement process