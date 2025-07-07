# Conduit MCP Usage Assistant

This file contains instructions for AI coding assistants to help users understand and effectively use Conduit's MCP capabilities with their Atlassian tools.

---

## To the AI Assistant

You are helping a user who has already set up Conduit's MCP server. Your role is to:
1. Provide an overview of Conduit's capabilities through MCP
2. Explain key use cases and workflows
3. Guide them through specific tasks they want to accomplish
4. Answer questions about features and best practices

**Important**: This guide focuses on using Conduit through the MCP interface in AI coding assistants, NOT the command-line interface.

## Overview of Conduit MCP Capabilities

### What is Conduit?

Conduit is an enterprise knowledge integration service that bridges AI coding assistants with Atlassian tools (Jira and Confluence). Through MCP, it provides:

- **Unified Access**: Single interface to both Jira and Confluence
- **AI-Optimized**: Responses formatted for AI understanding and processing
- **Multi-Site Support**: Work with multiple Atlassian instances seamlessly
- **Markdown Native**: Automatic conversion between markdown and Atlassian formats

### Available MCP Tools (15 total)

**Configuration & Discovery**:
1. `list_atlassian_sites` - View all configured Jira and Confluence sites

**Confluence Operations** (7 tools):
2. `get_confluence_page` - Retrieve page content by title in markdown format
3. `retrieve_confluence_hierarchy` - Get hierarchical page structure of a space
4. `create_confluence_page_from_markdown` - Create pages with markdown content
5. `update_confluence_page_from_markdown` - Update existing pages
6. `get_project_overview` - Unified view of project info from Jira & Confluence

**Jira Operations** (8 tools):
7. `search_jira_issues` - Search using JQL (Jira Query Language)
8. `create_jira_issue` - Create new issues with markdown descriptions
9. `update_jira_issue` - Update issue summary and description
10. `update_jira_status` - Transition issues between workflow states
11. `get_jira_boards` - List boards, optionally filtered by project
12. `get_jira_sprints` - Get sprints from a board
13. `add_issues_to_jira_sprint` - Add issues to active sprints
14. `create_jira_sprint` - Create new sprints with goals
15. `get_jira_remote_links` - View external links on issues

## Key Use Cases

### 1. Documentation Workflows

**Creating Technical Documentation**:
- "Create a Confluence page documenting our new API endpoints"
- "Update the architecture documentation with the latest design decisions"
- The AI can write markdown that's automatically converted to Confluence format

**Knowledge Discovery**:
- "Show me all documentation in the ARCH space about microservices"
- "Find our database schema documentation"
- "What's documented about our deployment process?"

**Maintaining Documentation**:
- "Update the setup guide with the new dependencies"
- "Add a troubleshooting section to the operations manual"
- Supports version conflict detection to prevent overwrites

### 2. Project Management

**Sprint Planning**:
- "Show me all unfinished stories from the last sprint"
- "Create a new sprint for the authentication feature"
- "Move these 5 stories into the current sprint"

**Issue Tracking**:
- "Find all critical bugs assigned to me"
- "Create a bug report for the login issue we just discovered"
- "Update the status of PROJ-123 to In Progress"

**Progress Monitoring**:
- "Show me what's currently in development"
- "List all issues completed this week"
- "What blockers do we have in the current sprint?"

### 3. Cross-Tool Workflows

**Requirements to Implementation**:
- Read requirements from Confluence
- Create corresponding Jira stories
- Link implementation details back to documentation

**Bug Investigation**:
- Search for related issues in Jira
- Find relevant documentation in Confluence
- Create new issues with full context

**Release Documentation**:
- Query completed issues for a version
- Generate release notes in Confluence
- Update project status pages

### 4. Team Collaboration

**Onboarding**:
- "Show me all onboarding documentation for new developers"
- "Create a Jira task for setting up John's development environment"
- "Find the coding standards documentation"

**Knowledge Sharing**:
- "Document the solution we just implemented for the caching issue"
- "Create a how-to guide for using our new CI/CD pipeline"
- "Find all documentation about our testing procedures"

## Common Tasks and Examples

### Working with Jira Issues

**Search for issues**:
```
"Find all open bugs in project ABC"
"Show me issues assigned to me in the current sprint"
"Search for issues mentioning 'performance' created this month"
```

**Create issues**:
```
"Create a new story in project XYZ for implementing user authentication"
"Create a bug report for the memory leak in the payment service"
"Create a task for updating the documentation"
```

**Update issues**:
```
"Update PROJ-123 with the investigation findings"
"Change the status of PROJ-456 to Code Review"
"Add the test results to issue PROJ-789"
```

### Working with Confluence

**Find documentation**:
```
"Show me the API documentation in the TECH space"
"Find the deployment guide for the production environment"
"Get the page about coding standards"
```

**Create documentation**:
```
"Create a new page documenting our Redis caching strategy"
"Create a troubleshooting guide for common Docker issues"
"Document the new feature we just implemented"
```

**Update documentation**:
```
"Update the setup guide with Python 3.12 requirements"
"Add a new section about error handling to the API docs"
"Update the architecture diagram on the system overview page"
```

### Sprint Management

**View sprint information**:
```
"Show me the active sprints for the Mobile team"
"What's in the current sprint for project ABC?"
"List all future sprints for the API board"
```

**Manage sprints**:
```
"Create a new 2-week sprint starting Monday"
"Add issues PROJ-123, PROJ-124, and PROJ-125 to sprint 45"
"Show me which board manages the Backend project"
```

## Best Practices

### 1. Use Natural Language
Conduit MCP is designed for natural conversation. Instead of memorizing commands, just describe what you want:
- ❌ "Execute search_jira_issues with parameter project = ABC"
- ✅ "Find all open issues in project ABC"

### 2. Leverage Markdown
When creating content, use rich markdown formatting:
- Headers, lists, and tables
- Code blocks with syntax highlighting
- Links and images (Confluence will handle conversion)

### 3. Be Specific with Searches
JQL (Jira Query Language) is powerful. Be specific:
- "Issues created this week" → `created >= -1w`
- "High priority bugs" → `priority = High AND type = Bug`
- "My team's work" → `team = "Backend" AND sprint in openSprints()`

### 4. Multi-Site Awareness
If you have multiple Atlassian sites, specify which one:
- "Search for issues in the production Jira"
- "Create a page in the staging Confluence"
- Sites are identified by their aliases in configuration

### 5. Incremental Updates
For large documentation updates:
1. First retrieve the current content
2. Make your changes
3. Update with version checking to prevent conflicts

## Troubleshooting

### "Site not found" Errors
- Check configured sites: "List all my Atlassian site aliases"
- Verify you're using the correct alias
- Ensure API token is configured for that site

### "Page not found" Errors
- Confluence pages are found by exact title match
- Check the space key is correct
- Try searching the hierarchy first

### "Permission denied" Errors
- Verify your Atlassian account has necessary permissions
- Check API token hasn't expired
- Ensure you have access to the specific space/project

### Search Returns No Results
- Verify JQL syntax is correct
- Check if you have permission to view those issues
- Try a broader search first, then narrow down

## Advanced Features

### 1. Image Attachments (Confluence)
When creating or updating pages, you can attach images:
```
"Create a new architecture overview page with the diagram I just created"
"Update the user guide with the new screenshots"
```

### 2. Confluence Hierarchy Navigation
Explore documentation structure:
```
"Show me the page hierarchy for the DOCS space"
"What child pages exist under 'Architecture'?"
"Find all pages under 'API Documentation' up to 3 levels deep"
```

### 3. Project Overview
Get unified information across tools:
```
"Give me an overview of project ABC including Jira stats and Confluence docs"
"Show me everything about the Authentication feature across both tools"
```

### 4. Bulk Operations
While each operation is individual, you can chain them:
```
"Find all bugs marked for release 2.0 and create a release notes page"
"Move all stories tagged 'frontend' to the next sprint"
```

## Getting Started Questions

To help you make the most of Conduit, I can assist with:

1. **Specific Tasks**: "How do I create a weekly status report from Jira data?"
2. **Workflow Design**: "What's the best way to track feature documentation?"
3. **Search Queries**: "How do I find all issues modified in the last month?"
4. **Automation Ideas**: "Can I automate creating Jira tickets from requirements?"
5. **Best Practices**: "What's the recommended way to organize Confluence spaces?"

## What would you like to explore?

Now that you understand Conduit's capabilities, what would you like to do? Some suggestions:

- 🔍 **Explore your data**: "Show me what's in my Jira projects"
- 📝 **Create documentation**: "Help me document a new feature"
- 🎯 **Manage work**: "What should I work on next?"
- 🔧 **Set up workflows**: "How can I improve my team's process?"
- ❓ **Learn more**: "Tell me more about [specific feature]"

Feel free to ask about any aspect of using Conduit with your Atlassian tools!