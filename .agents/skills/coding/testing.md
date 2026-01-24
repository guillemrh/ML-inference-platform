# Testing Standards

## Philosophy

- **All code changes require tests**
- Tests must be **fast** and **deterministic**
- Prefer focused unit tests over large integration tests
- Mock external dependencies

## Test Structure

```
backend/tests/
├── conftest.py          # Shared fixtures
├── test_health.py       # Health endpoint tests
├── test_inference.py    # Inference endpoint tests
└── test_models.py       # Model loading/inference tests
```

## Naming Conventions

```python
# Test files: test_<module>.py
test_health.py
test_inference.py

# Test classes: Test<Feature>
class TestHealthEndpoint:
    ...

# Test methods: test_<behavior>
def test_health_returns_200(self):
    ...

def test_inference_with_invalid_input_returns_422(self):
    ...
```

## Fixtures

Use pytest fixtures for common setup.

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """Test client for API requests."""
    return TestClient(app)

@pytest.fixture
def sample_input():
    """Sample valid input for inference."""
    return {"features": [1.0, 2.0, 3.0, 4.0]}
```

## API Tests

```python
class TestInferenceEndpoint:
    """Tests for /predict endpoint."""

    def test_predict_success(self, client, sample_input):
        """Test successful prediction request."""
        response = client.post("/predict", json=sample_input)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "model_version" in data
        assert "latency_ms" in data

    def test_predict_invalid_input(self, client):
        """Test prediction with invalid input returns 422."""
        response = client.post("/predict", json={})

        assert response.status_code == 422

    def test_predict_empty_features(self, client):
        """Test prediction with empty features list."""
        response = client.post("/predict", json={"features": []})

        assert response.status_code == 422
```

## Mocking

Mock external dependencies, not internal logic.

```python
from unittest.mock import Mock, patch

def test_inference_handles_model_error(client, sample_input):
    """Test graceful handling when model fails."""
    with patch("app.services.inference_service.model") as mock_model:
        mock_model.predict.side_effect = RuntimeError("Model error")

        response = client.post("/predict", json=sample_input)

        assert response.status_code == 500
        assert "Model inference failed" in response.json()["detail"]
```

## Test Speed

Tests should be fast. Guidelines:
- Unit tests: < 100ms each
- API tests: < 500ms each
- Total suite: < 30 seconds

```python
import time

def test_health_is_fast(client):
    """Health check should respond in under 100ms."""
    start = time.time()
    response = client.get("/health")
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 0.1, f"Health check took {elapsed:.2f}s"
```

## Running Tests

```bash
# Run all tests (via Docker)
docker-compose exec backend pytest -v

# Run specific test file
docker-compose exec backend pytest -v tests/test_health.py

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=term-missing

# Run tests matching pattern
docker-compose exec backend pytest -v -k "health"
```

## Test Requirements

Before any PR:
- [ ] All tests pass
- [ ] New code has tests
- [ ] No test relies on external services
- [ ] Tests are deterministic (same result every run)
