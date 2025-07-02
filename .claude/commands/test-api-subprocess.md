---
description: Execute comprehensive API testing using Claude subprocess for complex integrations
usage: /project:test-api-subprocess [TEST-DESCRIPTION]
example: /project:test-api-subprocess "Test the complete order processing API workflow with external payment gateway"
---

I'll execute comprehensive API testing using a Claude subprocess for autonomous test execution.

## Step 1: Prepare Test Context

### Gather API Information
!echo "Current branch: $(git branch --show-current)"
!find . -name "*.py" -path "*/routers/*" -o -path "*/endpoints/*" -o -path "*/controllers/*" | head -10
!grep -r "@app\." . --include="*.py" | head -5 || grep -r "@router\." . --include="*.py" | head -5

### Check Test Environment
!test -f requirements.txt && grep -E "(pytest|httpx|requests)" requirements.txt
!test -f .env.test && echo "Test environment file found" || echo "No test environment file"

## Step 2: Determine Test Scope

Based on the feature and acceptance criteria:
- API endpoints to test
- Integration points
- Authentication flows
- Data validation rules
- Error scenarios

## Step 3: Launch Subprocess Testing

I'll execute the API tests using a Claude subprocess:

```bash
claude -p "You are testing a Python backend API. Your task is to:

1. Analyze the API structure in [PROJECT_PATH]
2. Test the following API workflow: [SPECIFIC_WORKFLOW_DESCRIPTION]
3. Create comprehensive test cases covering:
   - Happy path scenarios
   - Authentication and authorization
   - Input validation (edge cases, invalid data)
   - Error handling (4xx and 5xx responses)
   - Data persistence and retrieval
   - Integration with external services

4. For each endpoint test:
   - All HTTP methods (GET, POST, PUT, DELETE)
   - Query parameters and filters
   - Pagination if applicable
   - Request body variations
   - Header requirements

5. Test data scenarios:
   - Empty data sets
   - Single items
   - Large data sets
   - Special characters and Unicode
   - SQL injection attempts
   - Maximum field lengths

6. Performance considerations:
   - Response time for typical requests
   - Behavior under concurrent requests
   - Rate limiting if implemented

7. Create test files using pytest following the project structure
8. Run the tests and document results
9. Generate a coverage report

Use the following test patterns:
- Unit tests for business logic
- Integration tests for API endpoints
- Mock external services appropriately
- Use fixtures for test data setup

Focus on: [SPECIFIC_REQUIREMENTS]" --dangerously-skip-permissions
```

## Step 4: Process Results

After subprocess execution:
- Review test execution output
- Analyze coverage report
- Identify failed tests
- Check for untested code paths

## Step 5: Create Test Report

Generate a comprehensive test report including:
- API endpoints tested
- Test coverage percentage
- Failed test details
- Performance metrics
- Security vulnerabilities found
- Recommendations for improvements

## When to Use This Command

Use subprocess API testing when:
- Testing complex multi-service integrations
- Need comprehensive edge case discovery
- Testing authentication/authorization flows
- Validating complex business logic
- External service integration testing
- Load and stress testing scenarios

## Example Complex API Flows

### E-commerce Order Processing
```bash
"Test order API: Create cart, add items, apply discounts, calculate tax, process payment, update inventory, send notifications, generate invoice"
```

### User Management System
```bash
"Test user APIs: Registration with validation, email verification, login/logout, password reset, profile updates, role changes, account deletion"
```

### Data Pipeline API
```bash
"Test data API: Upload file, validate format, transform data, trigger processing, monitor status, handle errors, retrieve results, cleanup"
```

## Integration Testing Patterns

### External Service Mocking
The subprocess will intelligently:
- Identify external dependencies
- Create appropriate mocks
- Test both success and failure scenarios
- Validate retry logic

### Database Transaction Testing
- Test rollback scenarios
- Verify data consistency
- Check constraint violations
- Test concurrent access

---

## 🚀 Next Steps After Subprocess Testing

After the subprocess completes:

1. **Review the comprehensive test report:**
   - Check test coverage percentage
   - Review any failed tests
   - Note security vulnerabilities found
   - Examine performance metrics

2. **If tests pass, proceed to complete:**
   ```
   /project:complete-feature [SITE-ALIAS]
   ```

3. **If issues found:**
   - Address security vulnerabilities first
   - Fix failing tests
   - Run `/project:test-feature` for focused re-testing
   - Or run this command again for another comprehensive scan

💡 **Tip:** Subprocess API testing often discovers security issues and edge cases that manual testing misses!