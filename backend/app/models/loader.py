"""
Model loader for Chemical Reactor Anomaly Detection.

Supports loading multiple model instances for shadow mode and canary deployments.
"""

from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.core.logging import get_logger

logger = get_logger(__name__)


class ModelLoadError(Exception):
    """Raised when model fails to load."""

    pass


class ModelNotLoadedError(Exception):
    """Raised when inference is attempted before model is loaded."""

    pass


class ReactorModel:
    """
    Wrapper for the reactor anomaly detection model.

    Loads model and scaler from disk, provides inference method.
    Each instance can hold a different model version.
    """

    def __init__(self, name: str = "primary") -> None:
        """
        Initialize model wrapper.

        Args:
            name: Identifier for this model instance (e.g., "primary", "shadow")
        """
        self._name = name
        self._model: Any = None
        self._scaler: Any = None
        self._feature_names: list[str] = []
        self._version: str = ""
        self._loaded: bool = False

    @property
    def name(self) -> str:
        """Get model instance name."""
        return self._name

    def load(self, model_path: Path, version: str | None = None) -> None:
        """
        Load model from disk.

        Args:
            model_path: Path to model file.
            version: Optional version override. If not provided, uses version from model file.

        Raises:
            ModelLoadError: If model file doesn't exist or fails to load.
        """
        if not model_path.exists():
            raise ModelLoadError(f"Model file not found: {model_path}")

        try:
            model_data = joblib.load(model_path)
            self._model = model_data["model"]
            self._scaler = model_data["scaler"]
            self._feature_names = model_data["feature_names"]
            self._version = version or model_data.get("version", "unknown")
            self._loaded = True

            logger.info(
                "Model loaded successfully",
                extra={
                    "extra_fields": {
                        "model_name": self._name,
                        "model_path": str(model_path),
                        "model_version": self._version,
                        "feature_names": self._feature_names,
                    }
                },
            )
        except Exception as e:
            raise ModelLoadError(f"Failed to load model '{self._name}': {e}") from e

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded

    @property
    def version(self) -> str:
        """Get model version."""
        return self._version

    @property
    def feature_names(self) -> list[str]:
        """Get expected feature names."""
        return self._feature_names

    def predict(self, features: list[float]) -> dict[str, Any]:
        """
        Make a prediction for the given features.

        Args:
            features: List of feature values in order:
                [temperature, pressure, flow_rate, reactant_concentration,
                 ph_level, stirrer_speed]

        Returns:
            Dict with prediction and probability.

        Raises:
            ModelNotLoadedError: If model hasn't been loaded.
            ValueError: If features have wrong shape.
        """
        if not self._loaded:
            raise ModelNotLoadedError("Model not loaded. Call load() first.")

        if len(features) != len(self._feature_names):
            raise ValueError(
                f"Expected {len(self._feature_names)} features, got {len(features)}. "
                f"Expected: {self._feature_names}"
            )

        # Reshape and scale
        X = np.array(features).reshape(1, -1)
        X_scaled = self._scaler.transform(X)

        # Predict
        prediction = int(self._model.predict(X_scaled)[0])
        probabilities = self._model.predict_proba(X_scaled)[0]
        probability = float(probabilities[prediction])

        return {
            "prediction": prediction,
            "probability": probability,
            "label": "anomaly" if prediction == 1 else "normal",
        }


