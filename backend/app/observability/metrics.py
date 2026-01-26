"""
Prometheus metrics definitions for ML inference platform.

Metrics follow Prometheus naming conventions:
- Counter names end with _total
- Histogram names end with _seconds
- Labels use snake_case
"""

from prometheus_client import Counter, Gauge, Histogram

# HTTP Request Metrics (for middleware)
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

# ML Inference Metrics
PREDICTIONS_TOTAL = Counter(
    "predictions_total",
    "Total predictions made",
    ["label"],  # "normal" or "anomaly"
)

INFERENCE_DURATION_SECONDS = Histogram(
    "inference_duration_seconds",
    "ML model inference duration in seconds",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)

# Model Info Metrics
MODEL_INFO = Gauge(
    "model_info",
    "Model metadata",
    ["version"],
)

MODEL_LOADED = Gauge(
    "model_loaded",
    "Whether the model is loaded (1) or not (0)",
)


def set_model_info(version: str, is_loaded: bool) -> None:
    """
    Update model info metrics.

    Call this at startup and whenever model status changes.

    Args:
        version: Model version string
        is_loaded: Whether model is loaded
    """
    MODEL_INFO.labels(version=version).set(1)
    MODEL_LOADED.set(1 if is_loaded else 0)


def record_prediction(label: str, duration_seconds: float) -> None:
    """
    Record a prediction event.

    Args:
        label: Prediction label ("normal" or "anomaly")
        duration_seconds: Time taken for inference
    """
    PREDICTIONS_TOTAL.labels(label=label).inc()
    INFERENCE_DURATION_SECONDS.observe(duration_seconds)
