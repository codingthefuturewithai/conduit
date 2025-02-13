# Manual Testing Guide for Jira Commands

This document provides a sequence of commands to manually test the Jira integration functionality, particularly focusing on multi-site support. These tests verify that all Jira operations work correctly across different site configurations.

## Prerequisites

1. Ensure you have conduit installed and configured
2. Configure at least one Jira site in your `~/.config/conduit/config.yaml`
3. Have a Jira project where you can create and modify issues

## Test Commands

Replace the following placeholders in the commands:

- `<site-alias>`: Your configured site alias (e.g., "site1", "prod", etc.)
- `<project-key>`: Your Jira project key (e.g., "PROJ", "TEST", etc.)
- `<issue-key>`: The issue key from the create command response (e.g., "PROJ-123")

### 1. Create Issue

```bash
conduit jira issue create --project <project-key> --summary "Test multi-site support" --description "Testing the multi-site support functionality" --type Task --site <site-alias>
```

### 2. Update Issue Description

```bash
conduit jira issue update <issue-key> --description "Testing the multi-site support functionality\n\nUpdate: Successfully verified that the multi-site support is working correctly with the site configuration." --site <site-alias>
```

### 3. Search for Issue

```bash
conduit jira issue search "key = <issue-key>" --site <site-alias>
```

### 4. Add Comment

```bash
conduit jira issue comment <issue-key> "Testing multi-site comment functionality" --site <site-alias>
```

### 5. Check Remote Links

```bash
conduit jira issue remote-links <issue-key> --site <site-alias>
```

### 6. Update Status

```bash
conduit jira issue status <issue-key> "Done" --site <site-alias>
```

## Expected Results

1. **Create**: Should return a JSON response with the new issue details
2. **Update**: Should confirm successful update
3. **Search**: Should return JSON data matching the issue
4. **Comment**: Should show success message and comment details
5. **Remote Links**: Should indicate no remote links found (if none added)
6. **Status**: Should show transition details and success message

## Troubleshooting

If any command fails:

1. Verify your site configuration in `~/.config/conduit/config.yaml`
2. Check that your API token has the necessary permissions
3. Ensure the issue exists and you have access to it
4. Verify that the status transition is valid for your project's workflow
