---
description: Complete a feature by committing changes, creating a PR, and updating JIRA
usage: /project:complete-feature [SITE-ALIAS]
example: /project:complete-feature saaga
---

I'll help you complete the current feature by committing changes, creating a pull request, and updating the JIRA issue.

## Parse Arguments
- Site alias provided: $ARGUMENTS (e.g., "saaga")
- I'll extract the JIRA issue key from the current branch name

## Step 1: Review Changes
First, let me check the current status:

!git status
!git diff --stat

## Step 2: Run Quality Checks
Running linting and tests before committing:

!ruff check .
!pytest

## Step 3: Stage and Commit Changes
I'll stage all changes and create a detailed commit message:

!git add -A

The commit message will follow conventional commits format and include:
- Brief description
- Detailed changes
- Reference to JIRA issue
- Claude Code attribution

## Step 4: Push Feature Branch
!git push -u origin $(git branch --show-current)

## Step 5: Create Pull Request
Using GitHub CLI to create the PR:

```bash
gh pr create \
  --title "feat: [Description based on commits]" \
  --body "## Summary
- Key changes implemented

## Related Issue
Closes [ISSUE-KEY from branch name]

## Test Plan
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Linting passes

🤖 Generated with [Claude Code](https://claude.ai/code)" \
  --assignee @me
```

## Step 6: Update JIRA to Done
After the PR is created, I'll:
1. Extract the JIRA issue key from the branch name (e.g., feature/ACT-123-description → ACT-123)
2. Add the PR link as a comment on the JIRA issue using mcp__mcp_jira__update_jira_issue with the provided site alias
3. Update the issue status to 'Done' using mcp__Conduit__update_jira_status with the site alias

Let's start by reviewing your changes...

---

## 🚀 Next Steps After PR Creation

Once your PR is created:

1. **Share PR with team:**
   - The PR URL will be displayed above
   - Share in Slack/Teams for review
   - JIRA issue will be automatically updated with PR link

2. **After PR approval and merge:**
   ```
   /project:post-merge
   ```
   This will:
   - Sync your main branch
   - Clean up the feature branch
   - Prepare for the next feature

3. **Start your next feature:**
   ```
   /project:start-feature [NEW-ISSUE-KEY] [SITE-ALIAS]
   ```

💡 **Tip:** Your JIRA issue is now marked as "Done" and linked to the PR!