"""
Admin API routes for traffic management.

Provides runtime control over canary traffic splitting.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.observability.metrics import CANARY_WEIGHT
from app.services import get_model_manager

router = APIRouter(prefix="/admin", tags=["admin"])
logger = get_logger(__name__)


class TrafficSplitRequest(BaseModel):
    """Request to update canary traffic weight."""

    canary_weight: int = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of traffic to route to canary (0-100)",
    )


class TrafficSplitResponse(BaseModel):
    """Current traffic split configuration."""

    canary_weight: int
    primary_weight: int
    canary_model_version: str | None
    primary_model_version: str | None


@router.get("/traffic-split", response_model=TrafficSplitResponse)
async def get_traffic_split() -> TrafficSplitResponse:
    """Get the current traffic split configuration."""
    mm = get_model_manager()
    split = mm.traffic_router.get_split()
    return TrafficSplitResponse(
        canary_weight=split.canary_weight,
        primary_weight=split.primary_weight,
        canary_model_version=mm.secondary.version if mm.secondary else None,
        primary_model_version=mm.primary.version if mm.primary else None,
    )


@router.post("/traffic-split", response_model=TrafficSplitResponse)
async def set_traffic_split(req: TrafficSplitRequest) -> TrafficSplitResponse:
    """
    Update the canary traffic weight at runtime.

    Set to 0 for instant rollback (all traffic to primary).
    Set to 100 to fully promote canary.
    """
    mm = get_model_manager()

    if not mm.canary_enabled:
        raise HTTPException(
            status_code=409,
            detail="Canary mode is not enabled. Set DEPLOYMENT_MODE=canary.",
        )

    mm.traffic_router.set_canary_weight(req.canary_weight)
    CANARY_WEIGHT.set(req.canary_weight)

    split = mm.traffic_router.get_split()
    return TrafficSplitResponse(
        canary_weight=split.canary_weight,
        primary_weight=split.primary_weight,
        canary_model_version=mm.secondary.version if mm.secondary else None,
        primary_model_version=mm.primary.version if mm.primary else None,
    )
