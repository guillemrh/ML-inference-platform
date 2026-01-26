"""Tests for Prometheus metrics and observability."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


class TestMetricsEndpoint:
    """Tests for /metrics endpoint."""

    def test_metrics_endpoint_returns_200(self):
        """Test that /metrics returns 200 OK."""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_endpoint_returns_prometheus_format(self):
        """Test that /metrics returns Prometheus text format."""
        response = client.get("/metrics")
        content_type = response.headers.get("content-type", "")
        assert "text/plain" in content_type

    def test_metrics_contains_http_metrics(self):
        """Test that HTTP request metrics are present."""
        # Make a request first to generate metrics
        client.get("/health")

        response = client.get("/metrics")
        content = response.text

        assert "http_requests_total" in content
        assert "http_request_duration_seconds" in content

    def test_metrics_contains_model_metrics(self):
        """Test that model info metrics are present."""
        response = client.get("/metrics")
        content = response.text

        assert "model_info" in content
        assert "model_loaded" in content


class TestHttpMetrics:
    """Tests for HTTP request metrics."""

    def test_health_request_recorded(self):
        """Test that health check is recorded in metrics."""
        client.get("/health")

        response = client.get("/metrics")
        content = response.text

        assert "http_requests_total" in content
        assert 'endpoint="/health"' in content

    def test_metrics_endpoint_not_counted(self):
        """Test that /metrics endpoint is not counted in HTTP metrics."""
        # Make several requests to /metrics
        for _ in range(3):
            client.get("/metrics")

        response = client.get("/metrics")
        content = response.text

        # /metrics should not appear as an endpoint label
        assert 'endpoint="/metrics"' not in content


class TestInferenceMetrics:
    """Tests for ML inference metrics."""

    @pytest.fixture
    def valid_input(self) -> dict:
        """Sample valid reactor input."""
        return {
            "temperature": 85.0,
            "pressure": 5.5,
            "flow_rate": 25.0,
            "reactant_concentration": 1.2,
            "ph_level": 7.0,
            "stirrer_speed": 300.0,
        }

    def test_prediction_increments_counter(self, valid_input: dict):
        """Test that successful prediction increments prediction counter."""
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 200

        metrics_response = client.get("/metrics")
        content = metrics_response.text

        assert "predictions_total" in content

    def test_prediction_records_duration(self, valid_input: dict):
        """Test that prediction records inference duration."""
        client.post("/predict", json=valid_input)

        metrics_response = client.get("/metrics")
        content = metrics_response.text

        assert "inference_duration_seconds" in content

    def test_prediction_labels_by_result(self, valid_input: dict):
        """Test that predictions are labeled by result (normal/anomaly)."""
        response = client.post("/predict", json=valid_input)
        result_label = response.json()["label"]

        metrics_response = client.get("/metrics")
        content = metrics_response.text

        assert f'label="{result_label}"' in content


class TestModelMetrics:
    """Tests for model info metrics."""

    def test_model_loaded_gauge_exists(self):
        """Test that model_loaded gauge exists in metrics."""
        response = client.get("/metrics")
        content = response.text

        # Gauge should exist (value set during lifespan startup)
        assert "model_loaded" in content

    def test_model_info_contains_version(self):
        """Test that model_info contains version label."""
        response = client.get("/metrics")
        content = response.text

        assert "model_info" in content
        assert 'version="' in content
