"""
Tests for health check endpoint.

These tests verify the most basic service functionality:
- The service can boot
- The health endpoint is reachable
- It returns the expected response
"""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    """
    Test client fixture.

    Creates a fresh FastAPI test client for each test.
    """
    app = create_app()
    return TestClient(app)


def test_health_check_returns_ok(client):
    """
    Test that /health returns 200 with correct status.

    This is the most critical test - if this fails, the service
    cannot be deployed or load balanced.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_is_fast(client):
    """
    Test that /health responds quickly.

    Health checks must be fast (<100ms) to avoid false positives
    in load balancer health probes.
    """
    import time

    start = time.time()
    response = client.get("/health")
    duration_ms = (time.time() - start) * 1000

    assert response.status_code == 200
    assert (
        duration_ms < 100
    ), f"Health check took {duration_ms:.2f}ms (should be <100ms)"
