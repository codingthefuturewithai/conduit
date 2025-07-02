# Workflow: Testing Backend APIs with PyTest

## Overview
This workflow describes how to use Claude to test Python backend APIs, particularly FastAPI applications, using pytest and related testing tools. This provides a testing approach for backend services that aren't MCP servers.

## Prerequisites
- Python environment with pytest installed
- API framework (FastAPI, Flask, Django REST, etc.)
- Test files following pytest conventions (`test_*.py` or `*_test.py`)
- API running locally or test fixtures configured

## Steps

### 1. Analyze API Structure
First, understand the API being tested:
```bash
# Look for API route definitions
find . -name "*.py" -type f | xargs grep -l "@app\|@router\|@api" | head -20

# Check for existing test structure
find . -path "*/test*" -name "*.py" | head -20

# Identify testing dependencies
grep -E "pytest|httpx|requests|fastapi\[all\]" requirements.txt || grep -E "pytest|httpx|requests|fastapi\[all\]" pyproject.toml
```

### 2. Understand Test Requirements
Based on the feature acceptance criteria:
- Identify API endpoints to test
- Determine request/response formats
- Note authentication requirements
- Plan test scenarios (happy path, error cases, edge cases)

### 3. Create or Update Test Files
Structure tests according to the feature:

#### Unit Tests for Business Logic
```python
# tests/unit/test_feature_logic.py
import pytest
from app.services.feature_service import process_data

def test_process_data_valid_input():
    result = process_data({"key": "value"})
    assert result["status"] == "success"

def test_process_data_invalid_input():
    with pytest.raises(ValueError):
        process_data({"invalid": "data"})
```

#### Integration Tests for API Endpoints
```python
# tests/integration/test_feature_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_resource():
    response = client.post(
        "/api/resources",
        json={"name": "test", "value": 123}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "test"

def test_get_resource():
    response = client.get("/api/resources/1")
    assert response.status_code == 200
    
def test_invalid_resource():
    response = client.get("/api/resources/999")
    assert response.status_code == 404
```

### 4. Test Authentication and Authorization
```python
# tests/integration/test_auth.py
def test_endpoint_requires_auth():
    response = client.get("/api/protected")
    assert response.status_code == 401

def test_endpoint_with_valid_token():
    headers = {"Authorization": "Bearer valid-token"}
    response = client.get("/api/protected", headers=headers)
    assert response.status_code == 200

def test_endpoint_with_invalid_permissions():
    headers = {"Authorization": "Bearer user-token"}
    response = client.post("/api/admin/action", headers=headers)
    assert response.status_code == 403
```

### 5. Test Data Validation
```python
# tests/integration/test_validation.py
@pytest.mark.parametrize("invalid_data,expected_error", [
    ({"name": ""}, "name must not be empty"),
    ({"name": "a" * 256}, "name too long"),
    ({"value": "not-a-number"}, "value must be numeric"),
    ({}, "required fields missing"),
])
def test_validation_errors(invalid_data, expected_error):
    response = client.post("/api/resources", json=invalid_data)
    assert response.status_code == 422
    assert expected_error in response.json()["detail"][0]["msg"]
```

### 6. Test Error Handling
```python
# tests/integration/test_error_handling.py
def test_database_error_handling(monkeypatch):
    def mock_db_error(*args, **kwargs):
        raise Exception("Database connection failed")
    
    monkeypatch.setattr("app.db.get_connection", mock_db_error)
    
    response = client.get("/api/resources")
    assert response.status_code == 500
    assert "Internal server error" in response.json()["detail"]
```

### 7. Run Tests with Coverage
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/integration/test_feature_endpoints.py

# Run tests matching pattern
pytest -k "test_create"

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run only marked tests
pytest -m "integration"
```

### 8. Performance Testing (Optional)
```python
# tests/performance/test_load.py
import pytest
import asyncio
import httpx
import time

@pytest.mark.asyncio
async def test_endpoint_performance():
    async with httpx.AsyncClient() as client:
        start_time = time.time()
        
        tasks = []
        for _ in range(100):
            task = client.get("http://localhost:8000/api/resources")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Should handle 100 requests in under 5 seconds
        assert duration < 5.0
```

### 9. Test Database Interactions
```python
# tests/integration/test_database.py
import pytest
from app.database import get_db
from app.models import Resource

@pytest.fixture
def test_db():
    # Setup test database
    db = get_db("test")
    yield db
    # Cleanup
    db.close()

def test_create_resource_in_db(test_db):
    resource = Resource(name="test", value=123)
    test_db.add(resource)
    test_db.commit()
    
    retrieved = test_db.query(Resource).filter_by(name="test").first()
    assert retrieved is not None
    assert retrieved.value == 123
```

### 10. Generate Test Report
After running tests, analyze the results:
```bash
# Generate detailed HTML report
pytest --html=report.html --self-contained-html

# Generate JUnit XML for CI/CD
pytest --junitxml=junit.xml

# Generate coverage badge
coverage-badge -o coverage.svg
```

## Best Practices

### Test Organization
- Group tests by feature or endpoint
- Use descriptive test names
- Keep tests independent and idempotent
- Use fixtures for common setup

### FastAPI Specific Tips
- Use `TestClient` for integration tests
- Test dependency injection
- Verify OpenAPI schema generation
- Test WebSocket endpoints if applicable

### Mocking and Fixtures
```python
@pytest.fixture
def mock_external_api():
    with responses.RequestsMock() as rsps:
        rsps.add(responses.GET, "https://api.external.com/data",
                 json={"result": "mocked"}, status=200)
        yield rsps

@pytest.fixture
def authenticated_client():
    client = TestClient(app)
    client.headers = {"Authorization": "Bearer test-token"}
    return client
```

### Testing Async Endpoints
```python
@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/async-endpoint")
    assert response.status_code == 200
```

## Common Test Patterns

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ({"x": 1, "y": 2}, 3),
    ({"x": 0, "y": 0}, 0),
    ({"x": -1, "y": 1}, 0),
])
def test_addition_endpoint(input, expected):
    response = client.post("/api/add", json=input)
    assert response.json()["result"] == expected
```

### Testing Pagination
```python
def test_pagination():
    # Create test data
    for i in range(25):
        client.post("/api/items", json={"name": f"item_{i}"})
    
    # Test first page
    response = client.get("/api/items?page=1&size=10")
    assert len(response.json()["items"]) == 10
    assert response.json()["total"] == 25
    assert response.json()["page"] == 1
```

### Testing File Uploads
```python
def test_file_upload():
    files = {"file": ("test.txt", "file content", "text/plain")}
    response = client.post("/api/upload", files=files)
    assert response.status_code == 200
    assert response.json()["filename"] == "test.txt"
```

## Troubleshooting

### Common Issues
- **Import errors**: Ensure PYTHONPATH includes project root
- **Database issues**: Use separate test database
- **Async test failures**: Use `pytest-asyncio` plugin
- **Fixture not found**: Check fixture scope and visibility

### Debugging Tests
```bash
# Run with Python debugger
pytest --pdb

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Run last failed tests first
pytest --ff
```