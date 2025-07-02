# Workflow: Post-Merge Actions

## Overview
This workflow describes the actions to take after a pull request has been reviewed and merged by the team. It ensures your local environment is synchronized and validates the merged changes.

## Prerequisites
- PR has been approved and merged to main branch
- Local development environment still has the feature branch
- Development environment is still properly configured
- You have records of which tests were run during feature development

## Steps

### 1. Sync Local Repository with Remote Main
```bash
# Switch to main branch
git checkout main

# Pull the latest changes including your merged PR
git pull origin main

# Verify your changes are included
git log --oneline -5
```

### 2. Re-run Feature Tests on Merged Code
Validate that the merge didn't introduce any issues by re-running the same tests you executed during feature development:

```bash
# Re-run the exact tests you used during development
# These should be the same tests that validated your feature before creating the PR

# Examples by project type:
# - For MCP features: See workflow 02-test-mcp-with-claude-subprocess.md
# - For web APIs: Run the same API tests or integration tests
# - For UI features: Run the same UI/component tests
# - For libraries: Run the same unit test suite
# - For CLI tools: Run the same command-line tests

# The key is consistency - whatever validated your feature during development
# should validate it again after merge
```

### 3. Run Project-Specific Quality Checks
Execute any code quality tools specific to your project:
```bash
# Run your project's linting/formatting checks
# Examples:
# - Python: ruff, black, mypy
# - JavaScript: eslint, prettier
# - Go: go fmt, golint
# - Rust: cargo fmt, clippy
# - Ruby: rubocop

# Run your project's standard quality command
[YOUR_LINT_COMMAND]
[YOUR_FORMAT_CHECK_COMMAND]
```

### 4. Clean Up Feature Branch
```bash
# Delete local feature branch
git branch -d feature/[ISSUE-KEY]-[description]

# If the branch wasn't fully merged (rare), use -D to force delete
# git branch -D feature/[ISSUE-KEY]-[description]

# Optional: Clean up remote tracking branches
git remote prune origin
```

### 5. Update Local Development Environment
```bash
# Ensure your development environment reflects the merged changes
# This varies by language/framework:

# Python: pip install -e ".[dev]" or pip install -r requirements.txt
# Node.js: npm install or yarn install
# Go: go mod download
# Rust: cargo build
# Ruby: bundle install
# Java: mvn install or gradle build

# Run your project's standard setup/install command
[YOUR_INSTALL_COMMAND]
```

### 6. Document Any Post-Merge Issues
If you discover any issues after merge:
```bash
# Create a new issue in your project tracking system
# Examples:
# - JIRA: Create a bug ticket linked to the original feature
# - GitHub Issues: Create a new issue referencing the merged PR
# - Linear: Create a bug issue with reference to the feature
# - Azure DevOps: Create a bug work item

# The key is to maintain traceability between the original feature and any issues found
```

## Best Practices
- Always sync with main before starting new work
- Run tests after pulling merged changes to catch integration issues early
- Clean up feature branches to keep repository tidy
- Document any post-merge discoveries for continuous improvement
- If issues are found, create new tickets rather than reopening completed ones

## Troubleshooting

### Merge Conflicts After Pull
If you encounter conflicts when pulling main:
```bash
# Stash any local changes
git stash

# Pull again
git pull origin main

# Apply stashed changes if needed
git stash pop
```

### Tests Failing on Main
If tests fail after pulling the merged code:
1. Verify you have the latest code: `git pull origin main`
2. Check if dependencies need updating
3. Look for recent merges that might conflict
4. Create a bug ticket if the issue persists

### Feature Branch Won't Delete
If git refuses to delete the feature branch:
```bash
# Check if there are unmerged commits
git log feature/[BRANCH_NAME] ^main

# Force delete if you're sure it's safe
git branch -D feature/[BRANCH_NAME]
```