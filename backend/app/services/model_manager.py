"""
Model manager for handling primary and shadow models.

Provides a central access point for all loaded models.
"""

from app.core.config import settings
from app.core.logging import get_logger
from app.models.loader import ModelLoadError, ReactorModel

logger = get_logger(__name__)


class ModelManager:
    """
    Manages primary and shadow model instances.

    Handles loading and provides access to models for inference.
    """

    def __init__(self) -> None:
        self._primary: ReactorModel | None = None
        self._shadow: ReactorModel | None = None

    @property
    def primary(self) -> ReactorModel | None:
        """Get the primary model."""
        return self._primary

    @property
    def shadow(self) -> ReactorModel | None:
        """Get the shadow model (may be None if shadow mode disabled)."""
        return self._shadow

    @property
    def shadow_enabled(self) -> bool:
        """Check if shadow mode is enabled and shadow model is loaded."""
        return (
            settings.shadow_enabled
            and self._shadow is not None
            and self._shadow.is_loaded
        )

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

    def load_shadow(self) -> None:
        """
        Load the shadow model if shadow mode is enabled.

        Does nothing if shadow mode is disabled.
        Logs warning but doesn't fail if shadow model can't be loaded.
        """
        if not settings.shadow_enabled:
            logger.info("Shadow mode disabled, skipping shadow model load")
            return

        try:
            self._shadow = ReactorModel(name="shadow")
            self._shadow.load(settings.shadow_model_path, settings.shadow_model_version)
            logger.info(
                "Shadow model loaded",
                extra={"extra_fields": {"version": self._shadow.version}},
            )
        except ModelLoadError as e:
            logger.warning(
                "Failed to load shadow model, continuing without shadow mode",
                extra={"extra_fields": {"error": str(e)}},
            )
            self._shadow = None

    def load_all(self) -> None:
        """Load primary model and shadow model (if enabled)."""
        self.load_primary()
        self.load_shadow()


# Global model manager instance
_model_manager: ModelManager | None = None


def get_model_manager() -> ModelManager:
    """Get the global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def get_model() -> ReactorModel:
    """
    Get the primary model.

    Convenience function for backwards compatibility.
    """
    manager = get_model_manager()
    if manager.primary is None:
        raise ModelLoadError("Primary model not loaded")
    return manager.primary
