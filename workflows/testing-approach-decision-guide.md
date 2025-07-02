# Testing Approach Decision Guide

## Overview
This guide helps developers and Claude Code choose between direct testing and subprocess testing for different scenarios. The choice depends on test complexity, scope, and objectives.

## Quick Decision Matrix

| Test Type | Simple/Deterministic | Complex/Exploratory |
|-----------|---------------------|---------------------|
| **MCP Tools** | Subprocess (always) | Subprocess (always) |
| **UI Testing** | Direct (`/project:test-ui`) | Subprocess (`/project:test-ui-subprocess`) |
| **API Testing** | Direct (`/project:test-api`) | Subprocess (`/project:test-api-subprocess`) |

## When to Use Subprocess Testing

### Always Use Subprocess
- **MCP Tool Testing**: All MCP tools benefit from autonomous agent execution
- **Natural Language Test Specs**: When JIRA contains conversational test descriptions
- **Exploratory Testing**: Finding edge cases and unexpected behaviors

### UI Testing - Use Subprocess When
- **Complex User Journeys**: Multi-page workflows (>5 steps)
- **Visual Validation**: Checking layout, design, responsive behavior
- **Cross-Browser Testing**: Testing on multiple browsers/devices
- **E2E Flows**: Full user scenarios from login to completion
- **Accessibility Testing**: Comprehensive ARIA and keyboard navigation
- **Dynamic Content**: Testing real-time updates, animations, AJAX

### API Testing - Use Subprocess When
- **Integration Testing**: Multiple services or external APIs
- **Complex Auth Flows**: OAuth, JWT, multi-factor authentication
- **Data Pipeline Testing**: Multi-step data processing workflows
- **Security Testing**: Comprehensive vulnerability scanning
- **Load Testing**: Concurrent requests and performance limits
- **Business Logic**: Complex rules with many edge cases

## When to Use Direct Testing

### UI Testing - Use Direct When
- **Component Testing**: Single component validation
- **Form Validation**: Simple input/output testing
- **Navigation Checks**: Basic routing verification
- **Smoke Tests**: Quick health checks
- **CI/CD Tests**: Fast, deterministic checks

### API Testing - Use Direct When
- **Unit Tests**: Testing individual functions
- **CRUD Operations**: Simple create/read/update/delete
- **Single Endpoints**: Testing one API route
- **Schema Validation**: Checking response formats
- **Quick Fixes**: Verifying bug fixes
- **Performance Benchmarks**: Measuring specific metrics

## Subprocess Testing Benefits

### Advantages
1. **Autonomous Exploration**: AI discovers edge cases you might miss
2. **Natural Language**: Write tests in plain English
3. **Comprehensive Coverage**: Tests scenarios beyond the happy path
4. **Visual Intelligence**: AI can interpret screenshots and UI state
5. **Adaptive Testing**: Handles unexpected states gracefully
6. **Detailed Reporting**: Rich test documentation and insights

### Trade-offs
1. **Execution Time**: Slower than direct testing
2. **Resource Usage**: Requires launching subprocess
3. **Less Control**: AI makes autonomous decisions
4. **Non-Deterministic**: Results may vary between runs

## Direct Testing Benefits

### Advantages
1. **Speed**: Fast execution for quick feedback
2. **Deterministic**: Same input → same output
3. **CI/CD Friendly**: Reliable for automated pipelines
4. **Precise Control**: Exact test specifications
5. **Resource Efficient**: Minimal overhead
6. **Debugging**: Easier to debug failures

### Trade-offs
1. **Limited Exploration**: Only tests what you specify
2. **Manual Coverage**: Must think of all edge cases
3. **Maintenance**: Tests need updates with code changes
4. **Less Adaptive**: Fails on unexpected states

## Examples

### Subprocess Testing Scenarios

#### Complex E-commerce Flow
```bash
/project:test-ui-subprocess "Test complete purchase: browse → search → filter → add to cart → checkout → payment → confirmation"
```

#### API Integration Testing
```bash
/project:test-api-subprocess "Test order processing with inventory, payment gateway, shipping API, and email notifications"
```

#### Security Testing
```bash
/project:test-api-subprocess "Test authentication endpoints for SQL injection, XSS, CSRF, and authorization bypasses"
```

### Direct Testing Scenarios

#### Simple Component Test
```bash
/project:test-ui
# Test that the login button is disabled when form is empty
```

#### Basic CRUD Test
```bash
/project:test-api
# Test GET /api/users returns 200 with user list
```

#### Quick Regression Test
```bash
/project:test-feature
# Verify fix for issue #123 - null pointer in user service
```

## Integration with CI/CD

### Recommended Pipeline Structure
```yaml
stages:
  - quick-tests:    # Direct testing - fast feedback
      - unit-tests
      - smoke-tests
      - lint-checks
  
  - deep-tests:     # Subprocess testing - comprehensive
      - integration-tests
      - e2e-flows
      - security-scans
  
  - deploy:
      - staging
      - production
```

## Best Practices

### For Subprocess Testing
1. **Clear Descriptions**: Provide detailed test objectives
2. **Time Budgets**: Set reasonable timeouts
3. **Save Artifacts**: Capture screenshots and logs
4. **Review Results**: AI findings need human validation
5. **Iterative Testing**: Refine based on discoveries

### For Direct Testing
1. **Fast Feedback**: Run frequently during development
2. **Specific Assertions**: Clear pass/fail criteria
3. **Test Data**: Use consistent fixtures
4. **Parallel Execution**: Maximize speed
5. **Continuous Updates**: Maintain with code changes

## Decision Flowchart

```
Start → Is it MCP testing?
  ├─ Yes → Use Subprocess
  └─ No → Check complexity
          ├─ Complex workflow? → Use Subprocess
          ├─ Visual validation? → Use Subprocess
          ├─ Exploratory needed? → Use Subprocess
          ├─ Multi-service integration? → Use Subprocess
          └─ None of above → Use Direct
```

## Summary

- **Subprocess Testing**: Best for complex, exploratory, and comprehensive testing
- **Direct Testing**: Best for quick, specific, and deterministic testing
- **Hybrid Approach**: Use both based on testing needs
- **MCP Testing**: Always use subprocess for MCP tools
- **Choose Wisely**: Consider time, resources, and test objectives