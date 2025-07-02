---
description: Test UI features using Puppeteer MCP server
usage: /project:test-ui [URL] [TEST-SCENARIO]
example: /project:test-ui http://localhost:3000 "login flow"
---

I'll test the UI at $ARGUMENTS using the Puppeteer MCP server.

## Step 1: Launch Browser
Using mcp__puppeteer__launch to start a browser session with:
- headless: false (so you can see the test execution)
- viewport: { width: 1280, height: 720 }

## Step 2: Navigate to Application
Using mcp__puppeteer__navigate to go to the specified URL and wait for it to load.

## Step 3: Execute Test Scenario
Based on the test scenario provided, I'll:
- Identify UI elements to interact with
- Perform user actions (clicks, form fills, navigation)
- Wait for expected results
- Take screenshots at key points
- Validate the outcomes

## Step 4: Generate Test Report
I'll provide:
- Step-by-step execution details
- Screenshots of important states
- Any errors encountered
- Performance metrics if relevant
- Recommendations for improvements

Common test scenarios I can handle:
- **Login/Authentication flows**
- **Form submissions and validation**
- **Navigation and routing**
- **Search functionality**
- **CRUD operations**
- **Responsive design checks**
- **Error handling scenarios**

Let me start the browser and begin testing...