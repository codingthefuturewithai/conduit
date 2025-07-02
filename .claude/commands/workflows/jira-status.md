---
description: Update JIRA issue status
usage: /project:workflows/jira-status [ISSUE-KEY] [STATUS] [SITE-ALIAS]
example: /project:workflows/jira-status ACT-123 "In Progress" saaga
---

Updating JIRA issue with the provided arguments.

## Parse Arguments
I'll extract from $ARGUMENTS:
- Issue key (e.g., ACT-123)
- New status (e.g., "In Progress")
- Site alias (e.g., saaga)

## Update Status
Use mcp__Conduit__update_jira_status to update the issue status using the provided site_alias

The status will be updated and I'll confirm the change was successful.