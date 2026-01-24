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

from app.api.routes import health, inference
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.models import ModelLoadError, get_model

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

    # Load model
    try:
        model = get_model()
        model.load()
        logger.info(
            "Model loaded at startup",
            extra={"extra_fields": {"model_version": model.version}},
        )
    except ModelLoadError as e:
        logger.error(
            "Failed to load model at startup",
            extra={"extra_fields": {"error": str(e)}},
        )
        # Don't fail startup - allow health checks to report degraded state

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

    # Register routes
    app.include_router(health.router, tags=["health"])
    app.include_router(inference.router, tags=["inference"])

    return app


# Application instance
app = create_app()
