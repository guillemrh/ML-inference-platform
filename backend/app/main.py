"""
FastAPI application entrypoint.

This is the main application file that:
- Configures logging
- Creates the FastAPI app
- Registers routes
- Handles startup/shutdown lifecycle
- Loads ML model at startup
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.routes import admin, health, inference
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.models import ModelLoadError
from app.observability import CANARY_WEIGHT, PrometheusMiddleware, set_model_info
from app.services import get_model_manager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Handles startup and shutdown logic, including model loading.
    """
    # Startup
    logger.info(
        "Application starting",
        extra={
            "extra_fields": {
                "app_name": settings.app_name,
                "environment": settings.environment,
            }
        },
    )

    # Load models
    try:
        model_manager = get_model_manager()
        model_manager.load_all()

        primary = model_manager.primary
        if primary:
            logger.info(
                "Primary model loaded at startup",
                extra={"extra_fields": {"model_version": primary.version}},
            )
            set_model_info(version=primary.version, is_loaded=True)

        secondary = model_manager.secondary
        if model_manager.shadow_enabled:
            logger.info(
                "Shadow mode enabled",
                extra={
                    "extra_fields": {
                        "secondary_version": secondary.version if secondary else None
                    }
                },
            )
        elif model_manager.canary_enabled:
            CANARY_WEIGHT.set(model_manager.traffic_router.canary_weight)
            logger.info(
                "Canary mode enabled",
                extra={
                    "extra_fields": {
                        "canary_version": secondary.version if secondary else None,
                        "canary_weight": model_manager.traffic_router.canary_weight,
                    }
                },
            )
    except ModelLoadError as e:
        logger.error(
            "Failed to load model at startup",
            extra={"extra_fields": {"error": str(e)}},
        )
        set_model_info(version=settings.model_version, is_loaded=False)

    yield

    # Shutdown
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """
    Application factory.

    Creates and configures the FastAPI application instance.

    Returns:
        Configured FastAPI application
    """
    # Setup logging first
    setup_logging()

    # Create app
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware)

    # Register routes
    app.include_router(health.router, tags=["health"])
    app.include_router(inference.router, tags=["inference"])
    app.include_router(admin.router)

    # Metrics endpoint
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Prometheus metrics endpoint."""
        return PlainTextResponse(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    return app


# Application instance
app = create_app()
