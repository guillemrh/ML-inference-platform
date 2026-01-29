"""
Traffic router for canary deployments.

Routes requests between primary and canary models based on
a configurable traffic weight.
"""

import random
import threading
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TrafficSplit:
    """Current traffic split configuration."""

    primary_weight: int
    canary_weight: int


class TrafficRouter:
    """
    Routes requests between primary and canary models.

    Thread-safe: weight can be updated at runtime via admin API.
    """

    def __init__(self, canary_weight: int = 0) -> None:
        self._lock = threading.Lock()
        self._canary_weight = canary_weight

    @property
    def canary_weight(self) -> int:
        with self._lock:
            return self._canary_weight

    def set_canary_weight(self, weight: int) -> None:
        """
        Update canary traffic weight.

        Args:
            weight: Percentage of traffic to route to canary (0-100).

        Raises:
            ValueError: If weight is not between 0 and 100.
        """
        if not 0 <= weight <= 100:
            raise ValueError("Canary weight must be between 0 and 100")
        with self._lock:
            old = self._canary_weight
            self._canary_weight = weight
        logger.info(
            "Canary weight updated",
            extra={"extra_fields": {"old_weight": old, "new_weight": weight}},
        )

    def get_split(self) -> TrafficSplit:
        """Get the current traffic split."""
        w = self.canary_weight
        return TrafficSplit(primary_weight=100 - w, canary_weight=w)

    def should_route_to_canary(self) -> bool:
        """Returns True if this request should go to the canary model."""
        return random.random() * 100 < self.canary_weight
