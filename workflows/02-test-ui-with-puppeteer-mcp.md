# Workflow: Testing UI with Puppeteer MCP

## Overview
This workflow describes how to use Claude with the Puppeteer MCP server to automate UI testing for web applications. This is an alternative to the MCP endpoint testing workflow for applications with user interfaces.

## Prerequisites
- Puppeteer MCP server configured and running
- Application running locally or accessible via URL
- Test scenarios identified based on acceptance criteria
- Basic understanding of CSS selectors and DOM structure

## Steps

### 1. Verify Puppeteer MCP Availability
```bash
# In a new Claude session, verify Puppeteer MCP is available
# Claude should be able to see tools like:
# - mcp__puppeteer__navigate
# - mcp__puppeteer__click
# - mcp__puppeteer__screenshot
# - mcp__puppeteer__evaluate
```

### 2. Prepare Test Scenarios
Based on the feature's acceptance criteria:
- Identify user flows to test
- Define expected outcomes
- Note critical UI elements (buttons, forms, etc.)
- Determine screenshot points for visual validation

### 3. Launch Browser Session
```
Use mcp__puppeteer__launch to start a browser session with options:
- headless: false (to see what's happening during development)
- viewport: { width: 1280, height: 720 }
```

### 4. Navigate to Application
```
Use mcp__puppeteer__navigate to go to [APPLICATION_URL]
Wait for the page to load completely
```

### 5. Execute Test Steps
For each test scenario:

#### Form Testing Example
```
1. Use mcp__puppeteer__fill to enter text in form fields
2. Use mcp__puppeteer__click to submit the form
3. Use mcp__puppeteer__wait_for_selector to wait for results
4. Use mcp__puppeteer__evaluate to check DOM state
5. Use mcp__puppeteer__screenshot to capture the result
```

#### Navigation Testing Example
```
1. Use mcp__puppeteer__click on navigation elements
2. Use mcp__puppeteer__get_url to verify navigation
3. Use mcp__puppeteer__wait_for_selector for page elements
4. Use mcp__puppeteer__screenshot for visual verification
```

### 6. Validate Results
- Compare screenshots with expected designs
- Verify text content matches requirements
- Check console for errors
- Validate form submissions and API calls

### 7. Document Test Results
Create a test report including:
- Test scenarios executed
- Pass/fail status for each scenario
- Screenshots of key states
- Any errors or unexpected behaviors
- Performance observations

## Examples

### Testing a Login Flow
```
1. Navigate to login page
2. Fill username field with test credentials
3. Fill password field
4. Click login button
5. Wait for dashboard to load
6. Verify user name appears in header
7. Screenshot the dashboard
```

### Testing a Search Feature
```
1. Navigate to search page
2. Enter search query
3. Click search button
4. Wait for results to load
5. Verify result count
6. Click on first result
7. Verify detail page loads
8. Screenshot the detail view
```

## Advanced Testing

### Responsive Design Testing
```
# Test different viewport sizes
Use mcp__puppeteer__set_viewport with sizes:
- Mobile: { width: 375, height: 667 }
- Tablet: { width: 768, height: 1024 }
- Desktop: { width: 1920, height: 1080 }
```

### Performance Testing
```
# Measure page load times
1. Use mcp__puppeteer__evaluate to access performance.timing
2. Calculate key metrics:
   - Time to first byte
   - DOM content loaded
   - Page load complete
```

### Accessibility Testing
```
# Check ARIA labels and keyboard navigation
1. Use mcp__puppeteer__evaluate to query ARIA attributes
2. Use mcp__puppeteer__keyboard to test tab navigation
3. Verify focus indicators are visible
```

## Best Practices
- Always start with headless: false during development
- Use data-testid attributes for reliable element selection
- Take screenshots at key points for debugging
- Test both happy paths and error scenarios
- Clean up sessions properly after testing
- Use explicit waits rather than arbitrary delays

## Troubleshooting

### Element Not Found
- Check if element is in iframe
- Verify selector is correct
- Add wait for element to appear
- Check if element is dynamically loaded

### Test Flakiness
- Add proper wait conditions
- Increase timeout values for slow operations
- Ensure consistent test data
- Check for race conditions

### Screenshot Issues
- Ensure viewport is set correctly
- Wait for animations to complete
- Check if lazy-loaded content is visible
- Use full-page screenshots when needed