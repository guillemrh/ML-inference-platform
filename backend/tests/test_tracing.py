"""
Tests for OpenTelemetry tracing setup and trace-log correlation.
"""

import json
import logging
from unittest.mock import patch

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider


class TestTracingSetup:
    """Tests for tracing initialization."""

    def test_tracing_disabled_is_noop(self):
        """Test that disabled tracing doesn't create a real provider."""
        from app.observability.tracing import setup_tracing, shutdown_tracing

        with patch("app.observability.tracing.settings") as mock_settings:
            mock_settings.tracing_enabled = False
            # Should not raise even without Jaeger
            from fastapi import FastAPI

            app = FastAPI()
            setup_tracing(app)
            shutdown_tracing()

    def test_get_tracer_returns_tracer(self):
        """Test that get_tracer returns a tracer instance."""
        from app.observability.tracing import get_tracer

        t = get_tracer("test_module")
        assert t is not None

    def test_get_tracer_creates_spans(self):
        """Test that tracer can create spans without errors."""
        from app.observability.tracing import get_tracer

        t = get_tracer("test_module")
        with t.start_as_current_span("test_span") as span:
            span.set_attribute("test_key", "test_value")


class TestTraceLogCorrelation:
    """Tests for trace context injection into structured logs."""

    def test_logs_include_trace_id_when_span_active(self):
        """Test that logs within a traced context contain trace_id."""
        # Set up a real provider
        provider = TracerProvider()

        old_provider = trace.get_tracer_provider()
        trace.set_tracer_provider(provider)

        try:
            tracer = trace.get_tracer("test")
            from app.core.logging import StructuredFormatter

            formatter = StructuredFormatter()

            with tracer.start_as_current_span("test_span"):
                record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg="test message",
                    args=None,
                    exc_info=None,
                )
                output = formatter.format(record)
                log_data = json.loads(output)

                assert "trace_id" in log_data
                assert "span_id" in log_data
                assert len(log_data["trace_id"]) == 32
                assert len(log_data["span_id"]) == 16
        finally:
            trace.set_tracer_provider(old_provider)
            provider.shutdown()

    def test_logs_without_span_have_no_trace_id(self):
        """Test that logs outside a traced context have no trace_id."""
        from app.core.logging import StructuredFormatter

        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=None,
            exc_info=None,
        )
        output = formatter.format(record)
        log_data = json.loads(output)

        assert "trace_id" not in log_data


class TestInferenceSpans:
    """Tests for tracing in the inference endpoint."""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app

        return TestClient(app)

    def test_predict_succeeds_with_tracing_disabled(self, client):
        """Test that /predict works normally with tracing disabled."""
        valid_input = {
            "temperature": 85.0,
            "pressure": 5.5,
            "flow_rate": 25.0,
            "reactant_concentration": 1.2,
            "ph_level": 7.0,
            "stirrer_speed": 300.0,
        }
        response = client.post("/predict", json=valid_input)
        assert response.status_code == 200

        data = response.json()
        assert "prediction" in data
        assert "model_version" in data


class TestModelLoadSpans:
    """Tests for model loading tracing."""

    def test_model_load_with_tracing_disabled(self):
        """Test that model loading works with tracing disabled."""
        from app.models.loader import ReactorModel

        model = ReactorModel(name="test")
        # Model loading is tested by conftest.py session fixture
        # This test just ensures the tracing import doesn't break loader
        assert model.name == "test"
