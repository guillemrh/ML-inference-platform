"""
ML Model Registry — FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health, models
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.database import create_tables

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Model Registry", extra={"extra_fields": {"environment": settings.environment}})
    create_tables()
    logger.info("Database tables ready")
    yield
    logger.info("Shutting down Model Registry")


app = FastAPI(
    title="ML Model Registry",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(models.router, prefix="/api/v1")
