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

# Shadow Mode Metrics
SHADOW_PREDICTIONS_TOTAL = Counter(
    "shadow_predictions_total",
    "Total shadow model predictions",
    ["status"],  # "success", "error", "timeout"
)

SHADOW_INFERENCE_DURATION_SECONDS = Histogram(
    "shadow_inference_duration_seconds",
    "Shadow model inference duration in seconds",
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)

SHADOW_PREDICTION_AGREEMENT = Counter(
    "shadow_prediction_agreement_total",
    "Count of predictions where shadow agreed/disagreed with primary",
    ["agreed"],  # "true" or "false"
)

SHADOW_LATENCY_DIFF_SECONDS = Histogram(
    "shadow_latency_diff_seconds",
    "Difference between shadow and primary latency (shadow - primary)",
    buckets=[-0.1, -0.05, -0.01, 0, 0.01, 0.05, 0.1, 0.25, 0.5],
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


def record_shadow_result(
    status: str,
    duration_seconds: float | None = None,
    agreed: bool | None = None,
    latency_diff_seconds: float | None = None,
) -> None:
    """
    Record shadow model execution result.

    Args:
        status: Result status ("success", "error", "timeout")
        duration_seconds: Shadow model inference time (if successful)
        agreed: Whether shadow agreed with primary (if successful)
        latency_diff_seconds: Shadow latency minus primary latency
    """
    SHADOW_PREDICTIONS_TOTAL.labels(status=status).inc()

    if duration_seconds is not None:
        SHADOW_INFERENCE_DURATION_SECONDS.observe(duration_seconds)

    if agreed is not None:
        SHADOW_PREDICTION_AGREEMENT.labels(agreed=str(agreed).lower()).inc()

    if latency_diff_seconds is not None:
        SHADOW_LATENCY_DIFF_SECONDS.observe(latency_diff_seconds)
