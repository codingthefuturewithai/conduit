---
description: Intelligently test a feature by automatically detecting whether to use MCP, API, or UI testing, and choosing between direct or subprocess execution
usage: /project:test-feature [OPTIONAL-HINTS]
example: /project:test-feature
---

I'll analyze the current feature and automatically determine the best testing approach.

## Step 1: Analyze Context

First, let me gather information to determine the testing approach:

### Check Current Branch
!git branch --show-current

### Analyze Recent Changes
!git diff --name-only HEAD~1..HEAD

### Look for Test Patterns
!find . -name "*.test.*" -o -name "*.spec.*" -o -name "*_test.*" | head -20

### Check Package Dependencies
!test -f package.json && grep -E "(puppeteer|playwright|selenium|jest|mocha|cypress)" package.json || echo "No package.json found"
!test -f requirements.txt && grep -E "(selenium|playwright|pytest)" requirements.txt || echo "No requirements.txt found"

## Step 2: Detection Logic

Based on the analysis, I'll determine the testing approach:

### Indicators for UI Testing (Puppeteer):
- Changes to files in: src/components/, src/pages/, src/views/, app/, frontend/
- File extensions: .jsx, .tsx, .vue, .svelte
- Presence of: package.json with React/Vue/Angular/Svelte
- JIRA issue mentions: UI, interface, button, form, page, screen, responsive
- Existing tests using: Puppeteer, Playwright, Cypress, Selenium

### Indicators for Backend API Testing (PyTest):
- Changes to files in: api/, backend/, routers/, endpoints/, controllers/
- File extensions: .py with FastAPI/Flask/Django decorators (@app.route, @router, @api_view)
- Presence of: FastAPI, Flask, Django REST in requirements.txt
- JIRA issue mentions: API, endpoint, REST, HTTP, request, response, validation
- Existing tests using: pytest, TestClient, httpx
- Files containing: test_*.py or *_test.py in tests/ directory

### Indicators for MCP Testing:
- Changes to files in: mcp/, tools/
- File extensions: .py with @mcp_server decorators
- Presence of: MCP server configuration
- JIRA issue mentions: MCP tool, integration with external services
- Current project is identified as MCP server

### Indicators for Hybrid Testing:
- Full-stack changes (both frontend and backend)
- JIRA issue mentions end-to-end functionality
- Changes span multiple layers

## Step 3: Determine Testing Approach (Direct vs Subprocess)

After detecting the test type, I'll determine whether to use direct testing or subprocess testing:

### Subprocess Testing Indicators:
- **Complex multi-step workflows** (>5 sequential actions)
- **Visual validation requirements** (UI appearance, layout)
- **Exploratory testing needs** (finding edge cases)
- **Cross-browser/cross-platform testing**
- **End-to-end flows spanning multiple pages/services**
- **Natural language test specifications in JIRA**
- **Need for autonomous test discovery**

### Direct Testing Indicators:
- **Simple CRUD operations**
- **Unit test level functionality**
- **Single endpoint/component testing**
- **Performance benchmarks**
- **Quick smoke tests**
- **CI/CD pipeline tests**
- **Deterministic test cases**

## Step 4: Execute Appropriate Testing

Based on my analysis, I'll proceed with the detected approach:

### If UI Testing Detected:
→ **Complex UI flows**: Using subprocess with `/project:test-ui-subprocess`
→ **Simple UI checks**: Using direct Puppeteer with `/project:test-ui`

### If Backend API Testing Detected:
→ **Complex integrations**: Using subprocess with `/project:test-api-subprocess`
→ **Simple endpoints**: Using direct pytest with `/project:test-api`

### If MCP Testing Detected:
→ Always using subprocess testing with `/project:test-mcp`
→ MCP tools benefit from autonomous agent execution

### If Hybrid Testing Needed:
→ Will test multiple layers:
  1. Backend API (choose direct/subprocess based on complexity)
  2. UI interactions (choose direct/subprocess based on flow)
  3. MCP tools if applicable (always subprocess)

### If Uncertain:
I'll analyze the JIRA issue acceptance criteria more carefully and may ask:
- "Would you prefer comprehensive subprocess testing or quick direct testing?"
- "Are there specific edge cases or exploratory scenarios to test?"

Let me begin the analysis...

---

## 🚀 Next Steps After Testing

After tests complete:

1. **If tests pass, complete the feature:**
   ```
   /project:complete-feature [SITE-ALIAS]
   ```
   This will commit your changes, create a PR, and update JIRA

2. **If tests fail:**
   - Fix the issues identified
   - Run `/project:test-feature` again
   - Repeat until tests pass

3. **For specific test types:**
   - UI issues? Try `/project:test-ui-subprocess` for deeper exploration
   - API issues? Try `/project:test-api-subprocess` for comprehensive testing
   - MCP issues? Review the subprocess output carefully

💡 **Tip:** The test command automatically detects the best testing approach based on your changes!