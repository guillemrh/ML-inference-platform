"""
OpenTelemetry tracing setup for the ML inference platform.

Configures trace provider, OTLP exporter, and FastAPI auto-instrumentation.
"""

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_provider: TracerProvider | None = None


def setup_tracing(app: FastAPI) -> None:
    """
    Initialize OpenTelemetry tracing.

    Sets up trace provider with OTLP exporter and instruments FastAPI.
    Does nothing if tracing is disabled.

    Args:
        app: FastAPI application instance to instrument.
    """
    global _provider

    if not settings.tracing_enabled:
        logger.info("Tracing disabled")
        return

    resource = Resource.create(
        {
            "service.name": settings.app_name,
            "service.version": "0.1.0",
            "deployment.environment": settings.environment,
        }
    )

    sampler = TraceIdRatioBased(settings.trace_sample_rate)
    _provider = TracerProvider(resource=resource, sampler=sampler)

    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint, insecure=True)
        _provider.add_span_processor(BatchSpanProcessor(exporter))
    except Exception as e:
        logger.warning(
            "Failed to configure OTLP exporter, traces will not be exported",
            extra={"extra_fields": {"error": str(e)}},
        )

    trace.set_tracer_provider(_provider)

    # Auto-instrument FastAPI for HTTP spans
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app)

    logger.info(
        "Tracing enabled",
        extra={
            "extra_fields": {
                "otlp_endpoint": settings.otlp_endpoint,
                "sample_rate": settings.trace_sample_rate,
            }
        },
    )


def shutdown_tracing() -> None:
    """Flush pending spans and shut down the trace provider."""
    global _provider
    if _provider is not None:
        _provider.shutdown()
        _provider = None


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance.

    Args:
        name: Tracer name (typically __name__ of the calling module).

    Returns:
        Tracer instance (NoOp if tracing is disabled).
    """
    return trace.get_tracer(name)
