---
description: Execute comprehensive UI testing using Claude subprocess for complex flows
usage: /project:test-ui-subprocess [TEST-DESCRIPTION]
example: /project:test-ui-subprocess "Test the complete user registration and onboarding flow"
---

I'll execute comprehensive UI testing using a Claude subprocess for autonomous test execution.

## Step 1: Prepare Test Context

### Gather Information
!echo "Current branch: $(git branch --show-current)"
!echo "Application URL: [Will need to determine from config or ask user]"

### Verify Puppeteer MCP Availability
I'll launch a subprocess that can use the Puppeteer MCP tools for UI testing.

## Step 2: Determine Test Scope

Based on the feature and JIRA issue, I'll identify:
- User flows to test
- Critical UI interactions
- Visual validation requirements
- Edge cases to explore

## Step 3: Launch Subprocess Testing

I'll execute the UI tests using a Claude subprocess:

```bash
claude -p "You are testing a web application UI. Use the Puppeteer MCP tools to:

1. Navigate to [APPLICATION_URL]
2. Test the following user flow: [SPECIFIC_FLOW_DESCRIPTION]
3. Take screenshots at key points:
   - Initial page load
   - After each major interaction
   - Final state
   - Any error states encountered

4. Verify the following:
   - All interactive elements work correctly
   - Form validations trigger appropriately
   - Navigation flows as expected
   - Visual elements render correctly
   - Responsive design works on different viewports

5. Test edge cases:
   - Invalid inputs
   - Rapid clicking
   - Browser back/forward navigation
   - Session timeout handling

6. Document your findings including:
   - Steps performed
   - Any errors or unexpected behaviors
   - Performance observations
   - Accessibility issues noticed

Use viewport sizes:
- Desktop: 1920x1080
- Tablet: 768x1024  
- Mobile: 375x667

Start with headless: false to observe the test execution." --dangerously-skip-permissions
```

## Step 4: Process Results

After subprocess execution:
- Review the test output
- Analyze screenshots captured
- Identify any failures or issues
- Create summary of test results

## Step 5: Create Test Report

Generate a comprehensive test report including:
- Test scenarios executed
- Pass/fail status
- Screenshots of key states
- Performance metrics
- Accessibility findings
- Recommendations for fixes

## When to Use This Command

Use subprocess UI testing when:
- Testing complex multi-page workflows
- Need visual regression validation
- Exploring edge cases autonomously
- Testing across multiple viewport sizes
- Natural language test cases from JIRA
- End-to-end user journey validation

## Example Complex Flows

### E-commerce Checkout
```bash
"Test complete checkout: Browse products, add to cart, apply coupon, enter shipping, select payment, complete order, verify confirmation"
```

### User Onboarding
```bash
"Test new user flow: Sign up, verify email, complete profile, tutorial walkthrough, first action, dashboard familiarization"
```

### Admin Dashboard
```bash
"Test admin capabilities: Login as admin, manage users, configure settings, generate reports, handle notifications, test permissions"
```

---

## 🚀 Next Steps After Subprocess Testing

After the subprocess completes:

1. **Review the test output:**
   - Check for any failures or unexpected behaviors
   - Review screenshots for visual issues
   - Note any performance concerns

2. **If tests pass, proceed to complete:**
   ```
   /project:complete-feature [SITE-ALIAS]
   ```

3. **If issues found:**
   - Fix the identified problems
   - Run `/project:test-feature` for quick re-test
   - Or run this command again for another deep exploration

💡 **Tip:** Subprocess testing excels at finding edge cases and visual issues you might miss!