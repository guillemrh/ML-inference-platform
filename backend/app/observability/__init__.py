"""Observability: metrics, tracing, and monitoring."""

from app.observability.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
    INFERENCE_DURATION_SECONDS,
    MODEL_INFO,
    MODEL_LOADED,
    PREDICTIONS_TOTAL,
    record_prediction,
    set_model_info,
)
from app.observability.middleware import PrometheusMiddleware

__all__ = [
    # Metrics
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_DURATION_SECONDS",
    "PREDICTIONS_TOTAL",
    "INFERENCE_DURATION_SECONDS",
    "MODEL_INFO",
    "MODEL_LOADED",
    # Helper functions
    "set_model_info",
    "record_prediction",
    # Middleware
    "PrometheusMiddleware",
]
