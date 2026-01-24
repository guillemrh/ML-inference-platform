"""
FastAPI application entrypoint.

This is the main application file that:
- Configures logging
- Creates the FastAPI app
- Registers routes
- Handles startup/shutdown lifecycle
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import health

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.

    Handles startup and shutdown logic.
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

    return app


# Application instance
app = create_app()
