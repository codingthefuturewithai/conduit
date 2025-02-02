Conduit is a tool for interacting with enterprise knowledge platforms (Jira, Confluence, GitHub, etc).
You can use it to help users manage their issues in Jira.
Here's how to use it:

# Jira Commands

## Get Issue

Syntax:
conduit jira issue get <issue_key>

Example:
conduit jira issue get PROJ-123

## Create Issue

Syntax:
conduit jira issue create --project <project_key> --summary <title> --description <details> --type <issue_type>

Note: Only use these issue types unless directed otherwise by the user:

- Task
- Story
- Bug

Example:
conduit jira issue create --project PROJ --summary "Add login feature" --description "Implement OAuth login" --type Task

## Add Comment

Syntax:
conduit jira issue comment <issue_key> <comment_text>

Example:
conduit jira issue comment PROJ-123 "PR is ready for review"

## Update Status

Syntax:
conduit jira issue status <issue_key> <status>

Example:
conduit jira issue status PROJ-123 "In Progress"

Note: Only use these status values unless directed otherwise by the user:

- To Do
- In Progress
- Done

# Response Format

When getting an issue (conduit jira issue get), the response includes:

- Issue details (key, project)
- Current status
- Description
- Comments
- Other metadata
