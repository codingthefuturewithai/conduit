# Workflow: Completing a Feature

## Overview
This workflow describes how to complete a feature by committing changes, creating a pull request, and updating the JIRA issue status.

## Prerequisites
- All implementation complete and tested
- Code reviewed locally (linting, formatting)
- All tests passing
- Git configured with appropriate remotes

## Steps

### 1. Stage and Commit Changes
```bash
# Stage all changes
git add -A

# Create detailed commit message following conventional commits
git commit -m "feat: [Brief description]

- [Detailed change 1]
- [Detailed change 2]
- [Additional details]

[Optional: BREAKING CHANGE: Description]
[Optional: Closes #issue]

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 2. Push Feature Branch
```bash
# Push the feature branch to remote
git push origin feature/[ISSUE-KEY]-[description]

# If this is the first push of the branch
git push -u origin feature/[ISSUE-KEY]-[description]
```

### 3. Create Pull Request
```bash
# Using GitHub CLI
gh pr create \
  --title "feat: [Brief description matching commit]" \
  --body "## Summary
- [Key change 1]
- [Key change 2]

## Related Issue
Closes [ISSUE-KEY]

## Test Plan
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Review Checklist
- [ ] Code follows project standards
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No sensitive data exposed

🤖 Generated with [Claude Code](https://claude.ai/code)" \
  --assignee @me
```

### 4. Update JIRA Issue
After PR is created, add PR link to JIRA:
```bash
# Add PR link as a comment
claude -p "Add a comment to JIRA issue [ISSUE-KEY] with the PR link: [PR_URL]"

# Or update the issue status if merging directly
claude -p "Use mcp__Conduit__update_jira_status to update [ISSUE-KEY] to 'In Review' status"
```

### 5. Post-Merge Actions
Once PR is approved and merged:
```bash
# Update JIRA to Done
claude -p "Use mcp__Conduit__update_jira_status to update [ISSUE-KEY] to 'Done' status using site_alias:[SITE]"

# Clean up local branch
git checkout main
git pull origin main
git branch -d feature/[ISSUE-KEY]-[description]
```

## Alternative: Direct Merge to Main
**⚠️ Use only for small teams or personal projects**

```bash
# After committing changes
git checkout main
git merge feature/[ISSUE-KEY]-[description]
git push origin main

# Then update JIRA
claude -p "Update [ISSUE-KEY] to 'Done' status"
```

## Commit Message Templates

### Feature
```
feat: Add user authentication system

- Implement JWT token generation
- Add login/logout endpoints
- Create user session management
- Add authentication middleware

Closes ACT-123
```

### Bug Fix
```
fix: Resolve pagination issue in search results

- Fix off-by-one error in page calculation
- Handle empty result sets correctly
- Add boundary condition tests

Fixes BUG-456
```

### Breaking Change
```
feat!: Redesign API response format

- Change response wrapper structure
- Update all endpoints to new format
- Add migration guide

BREAKING CHANGE: API responses now use 'data' wrapper instead of direct results

Closes API-789
```

## Best Practices
- Write clear, descriptive commit messages
- Reference JIRA issue in commits and PRs
- Ensure all tests pass before creating PR
- Add reviewers familiar with the code area
- Update documentation with significant changes
- Clean up feature branches after merge
- Keep JIRA status synchronized with actual progress

## GitHub CLI Options
```bash
# Create draft PR
gh pr create --draft

# Add specific reviewers
gh pr create --reviewer user1,user2

# Add labels
gh pr create --label "enhancement,needs-review"

# Target specific base branch
gh pr create --base develop
```