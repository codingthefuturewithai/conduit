---
description: Test Python backend API endpoints using pytest
usage: /project:test-api [ENDPOINT-PATTERN] [TEST-TYPE]
example: /project:test-api /api/users all
---

I'll test the backend API using pytest, focusing on $ARGUMENTS.

## Step 1: Analyze API Structure

First, let me understand the API structure:

### Find API endpoints
!find . -name "*.py" -type f | xargs grep -l "@app\|@router\|@api" | grep -v __pycache__ | head -20

### Check existing tests
!find . -path "*/test*" -name "*.py" | grep -v __pycache__ | head -20

### Review test configuration
!test -f pytest.ini && cat pytest.ini || echo "No pytest.ini found"
!test -f pyproject.toml && grep -A 10 "\[tool.pytest" pyproject.toml || echo "No pytest config in pyproject.toml"

## Step 2: Determine Test Scope

Based on the arguments and current changes, I'll focus on:
- Endpoint patterns to test
- Test types: unit, integration, or all
- Authentication requirements
- Data validation scenarios

## Step 3: Create/Update Tests

I'll create appropriate test files based on the feature:

### For new endpoints:
- Create test file in tests/integration/
- Write tests for all HTTP methods
- Include validation tests
- Add error handling tests

### For modified endpoints:
- Update existing tests
- Add tests for new functionality
- Ensure backward compatibility

## Step 4: Run Tests

### Execute pytest with appropriate options:
!pytest -v  # Verbose output

### Run with coverage:
!pytest --cov=app --cov-report=term-missing

### Run specific tests if needed:
!pytest -k "$ARGUMENTS" -v

## Step 5: Analyze Results

I'll review:
- Test pass/fail status
- Coverage report
- Performance metrics
- Any unexpected failures

## Common Test Scenarios

I can help test:
- **CRUD Operations**: Create, Read, Update, Delete endpoints
- **Authentication**: Token validation, permissions
- **Validation**: Request body validation, query parameters
- **Error Handling**: 4xx and 5xx responses
- **Pagination**: Limit/offset, cursor-based
- **Filtering**: Query parameters, search
- **File Operations**: Upload, download
- **Async Endpoints**: Background tasks, WebSockets

Let me begin analyzing your API...