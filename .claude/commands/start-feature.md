---
description: Start work on a new JIRA feature by fetching the issue, creating a branch, and updating status
usage: /project:start-feature [ISSUE-KEY] [SITE-ALIAS]
example: /project:start-feature ACT-123 saaga
---

I'll help you start working on JIRA issue $ARGUMENTS. Let me parse the issue key and site alias, then fetch the issue details and set up your development environment.

## Parse Arguments
Let me extract the issue key and site alias from the provided arguments:
- Arguments provided: $ARGUMENTS
- Expected format: [ISSUE-KEY] [SITE-ALIAS] (e.g., "ACT-123 saaga")

## Step 1: Fetch JIRA Issue
I'll use the parsed issue key and site alias to fetch the JIRA issue:
- Use mcp__mcp_jira__search_jira_issues to search for the issue
- The JQL query will be: key = [ISSUE-KEY]
- Using the provided site_alias

## Step 2: Create Feature Branch
After reviewing the issue, I'll create an appropriate feature branch:

!git checkout -b feature/[ISSUE-KEY]-<brief-description>

(The branch name will use the issue key and a brief description based on the issue summary)

## Step 3: Update JIRA Status
Use mcp__Conduit__update_jira_status to update the issue to 'In Progress' status using the provided site_alias

## Step 4: Research Technical Requirements
If needed, I'll use Context7 to research any unfamiliar technologies mentioned in the issue.

## Step 5: Determine Testing Approach
Based on the issue details and acceptance criteria, I'll identify the testing strategy:
- **UI Testing**: If the feature involves user interfaces, forms, or visual elements
- **MCP Testing**: If the feature involves API endpoints, tools, or integrations
- **Hybrid**: If the feature spans both frontend and backend

## Step 6: Create Implementation Plan
Based on the issue's acceptance criteria, I'll create a detailed implementation plan including:
- Overview of the approach
- Components to modify/create
- Implementation order
- Testing strategy (UI testing with Puppeteer, MCP testing, or both)
- Any risks or dependencies

## Step 6: Request Human Review
I'll present the implementation plan and wait for your approval before proceeding with exit_plan_mode.

Let's begin by fetching the JIRA issue details...

---

## 🚀 Next Steps After Approval

Once you approve the plan and implement the feature:

1. **Test your implementation:**
   ```
   /project:test-feature
   ```
   This will intelligently detect and run appropriate tests (UI, API, or MCP)

2. **When tests pass, complete the feature:**
   ```
   /project:complete-feature $SITE_ALIAS
   ```
   This will commit, create a PR, and update JIRA to "Done"

3. **After PR is merged:**
   ```
   /project:post-merge
   ```
   This will sync your main branch and clean up

💡 **Tip:** Save your site alias - you'll need it for the complete-feature command!