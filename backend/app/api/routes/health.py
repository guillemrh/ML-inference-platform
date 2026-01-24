"""
Health check endpoint.

Used by orchestrators, load balancers, and monitoring systems
to verify the service is running and ready to accept requests.
"""

from fastapi import APIRouter
from typing import Dict

from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.

    Returns:
        Status object indicating service is operational

    Notes:
        - Must be fast (<10ms)
        - No heavy dependencies
        - No database calls
        - Used by load balancers for readiness probes
    """
    logger.debug("Health check called")
    return {"status": "ok"}
