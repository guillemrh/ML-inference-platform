"""Tests for the registry client."""

from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from app.clients.registry_client import RegistryClient, RegistryModelInfo


@pytest.fixture
def client():
    return RegistryClient("http://registry:8001")


class TestGetActiveModel:
    def test_returns_model_info_on_success(self, client):
        mock_request = httpx.Request("GET", "http://registry:8001/api/v1/models/active")
        mock_response = httpx.Response(
            200,
            json={
                "model_id": 1,
                "name": "reactor_model",
                "version": "v1",
                "file_path": "/app/models/reactor_model_v1.pkl",
                "deployment_mode": "primary",
                "activated_at": "2026-01-01T00:00:00",
            },
            request=mock_request,
        )
        with patch.object(httpx, "get", return_value=mock_response):
            result = client.get_active_model("reactor_model", "primary")

        assert isinstance(result, RegistryModelInfo)
        assert result.version == "v1"
        assert result.file_path == Path("/app/models/reactor_model_v1.pkl")

    def test_returns_none_on_404(self, client):
        mock_response = httpx.Response(404, json={"detail": "not found"})
        with patch.object(httpx, "get", return_value=mock_response):
            result = client.get_active_model("nonexistent", "primary")

        assert result is None

    def test_returns_none_on_connection_error(self, client):
        with patch.object(httpx, "get", side_effect=httpx.ConnectError("refused")):
            result = client.get_active_model("reactor_model", "primary")

        assert result is None


class TestHealthCheck:
    def test_healthy(self, client):
        mock_response = httpx.Response(200, json={"status": "healthy"})
        with patch.object(httpx, "get", return_value=mock_response):
            assert client.health_check() is True

    def test_unreachable(self, client):
        with patch.object(httpx, "get", side_effect=httpx.ConnectError("refused")):
            assert client.health_check() is False
