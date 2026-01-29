"""
Model manager for handling primary and secondary models.

Provides a central access point for all loaded models and traffic routing.
"""

from app.core.config import settings
from app.core.logging import get_logger
from app.models.loader import ModelLoadError, ReactorModel
from app.services.traffic_router import TrafficRouter

logger = get_logger(__name__)


class ModelManager:
    """
    Manages primary and secondary model instances.

    The secondary model is used as shadow or canary depending on deployment_mode.
    """

    def __init__(self) -> None:
        self._primary: ReactorModel | None = None
        self._secondary: ReactorModel | None = None
        self._traffic_router = TrafficRouter(canary_weight=settings.canary_weight)

    @property
    def primary(self) -> ReactorModel | None:
        """Get the primary model."""
        return self._primary

    @property
    def secondary(self) -> ReactorModel | None:
        """Get the secondary model (may be None if not loaded)."""
        return self._secondary

    @property
    def deployment_mode(self) -> str:
        """Get the current deployment mode."""
        return settings.deployment_mode

    @property
    def shadow_enabled(self) -> bool:
        """Check if shadow mode is active."""
        return (
            settings.deployment_mode == "shadow"
            and self._secondary is not None
            and self._secondary.is_loaded
        )

    @property
    def canary_enabled(self) -> bool:
        """Check if canary mode is active."""
        return (
            settings.deployment_mode == "canary"
            and self._secondary is not None
            and self._secondary.is_loaded
        )

    @property
    def traffic_router(self) -> TrafficRouter:
        """Get the traffic router for canary deployments."""
        return self._traffic_router

    def load_primary(self) -> None:
        """
        Load the primary model.

        Raises:
            ModelLoadError: If model fails to load.
        """
        self._primary = ReactorModel(name="primary")
        self._primary.load(settings.model_path, settings.model_version)
        logger.info(
            "Primary model loaded",
            extra={"extra_fields": {"version": self._primary.version}},
        )

    def load_secondary(self) -> None:
        """
        Load the secondary model if deployment mode requires it.

        Does nothing in direct mode.
        Logs warning but doesn't fail if secondary model can't be loaded.
        """
        if settings.deployment_mode == "direct":
            logger.info("Direct mode, skipping secondary model load")
            return

        try:
            self._secondary = ReactorModel(name="secondary")
            self._secondary.load(
                settings.secondary_model_path, settings.secondary_model_version
            )
            logger.info(
                "Secondary model loaded",
                extra={
                    "extra_fields": {
                        "version": self._secondary.version,
                        "deployment_mode": settings.deployment_mode,
                    }
                },
            )
        except ModelLoadError as e:
            logger.warning(
                "Failed to load secondary model, falling back to direct mode",
                extra={"extra_fields": {"error": str(e)}},
            )
            self._secondary = None

    def load_all(self) -> None:
        """Load primary model and secondary model (if needed)."""
        self.load_primary()
        self.load_secondary()


# Global model manager instance
_model_manager: ModelManager | None = None


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def get_model() -> ReactorModel:
    """Get the primary model."""
    manager = get_model_manager()
    if manager.primary is None:
        raise ModelLoadError("Primary model not loaded")
    return manager.primary
