"""
Shadow runner for parallel model execution.

Executes primary and shadow models concurrently, comparing results
without affecting the primary response.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.models.loader import ReactorModel
from app.observability.tracing import get_tracer

logger = get_logger(__name__)
tracer = get_tracer(__name__)


@dataclass
class ModelResult:
    """Result from a single model execution."""

    prediction: int
    probability: float
    label: str
    latency_ms: float
    model_version: str
    success: bool = True
    error: str | None = None


@dataclass
class ShadowComparison:
    """Comparison between primary and shadow model results."""

    primary: ModelResult
    shadow: ModelResult | None
    predictions_agree: bool | None
    latency_diff_ms: float | None


def _run_model_sync(model: ReactorModel, features: list[float]) -> ModelResult:
    """
    Execute model prediction synchronously.

    Args:
        model: The model to run.
        features: Input features.

    Returns:
        ModelResult with prediction or error.
    """
    start = time.perf_counter()
    try:
        result = model.predict(features)
        latency_ms = (time.perf_counter() - start) * 1000
        return ModelResult(
            prediction=result["prediction"],
            probability=result["probability"],
            label=result["label"],
            latency_ms=latency_ms,
            model_version=model.version,
            success=True,
        )
    except Exception as e:
        latency_ms = (time.perf_counter() - start) * 1000
        return ModelResult(
            prediction=-1,
            probability=0.0,
            label="error",
            latency_ms=latency_ms,
            model_version=model.version,
            success=False,
            error=str(e),
        )


async def _run_model_async(
    model: ReactorModel, features: list[float], model_name: str = "primary"
) -> ModelResult:
    """
    Execute model prediction asynchronously with tracing.

    Wraps synchronous model execution in asyncio executor.
    """
    with tracer.start_as_current_span("model.predict") as span:
        span.set_attribute("model_name", model_name)
        span.set_attribute("model_version", model.version)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _run_model_sync, model, features)

        span.set_attribute("success", result.success)
        span.set_attribute("latency_ms", result.latency_ms)
        if result.success:
            span.set_attribute("prediction", result.prediction)
        elif result.error:
            span.set_attribute("error", result.error)

        return result


class ShadowRunner:
    """
    Runs primary and shadow models in parallel.

    The shadow model runs concurrently with the primary model.
    Shadow failures or timeouts don't affect the primary response.
    Results are compared and logged for analysis.
    """

    def __init__(
        self,
        primary_model: ReactorModel,
        shadow_model: ReactorModel | None = None,
        shadow_timeout_ms: int | None = None,
    ) -> None:
        """
        Initialize shadow runner.

        Args:
            primary_model: The primary model that serves responses.
            shadow_model: Optional shadow model for comparison.
            shadow_timeout_ms: Max time to wait for shadow model.
        """
        self._primary = primary_model
        self._shadow = shadow_model
        self._shadow_timeout_ms = shadow_timeout_ms or settings.shadow_timeout_ms

    async def run(self, features: list[float]) -> ShadowComparison:
        """
        Run inference on primary and shadow models.

        Primary model always runs. Shadow model runs in parallel if configured.
        Shadow failures don't affect the primary result.

        Args:
            features: Input features for prediction.

        Returns:
            ShadowComparison with both results.
        """
        # Always run primary
        primary_task = asyncio.create_task(
            _run_model_async(self._primary, features, model_name="primary")
        )

        # Run shadow if available
        shadow_result: ModelResult | None = None
        if self._shadow is not None:
            shadow_task = asyncio.create_task(
                _run_model_async(self._shadow, features, model_name="shadow")
            )

            # Wait for primary first (it determines response)
            primary_result = await primary_task

            # Wait for shadow with timeout
            try:
                shadow_result = await asyncio.wait_for(
                    shadow_task,
                    timeout=self._shadow_timeout_ms / 1000,
                )
            except asyncio.TimeoutError:
                shadow_result = ModelResult(
                    prediction=-1,
                    probability=0.0,
                    label="timeout",
                    latency_ms=self._shadow_timeout_ms,
                    model_version=self._shadow.version,
                    success=False,
                    error=f"Shadow model timed out after {self._shadow_timeout_ms}ms",
                )
                logger.warning(
                    "Shadow model timed out",
                    extra={
                        "extra_fields": {
                            "timeout_ms": self._shadow_timeout_ms,
                            "shadow_version": self._shadow.version,
                        }
                    },
                )
        else:
            primary_result = await primary_task

        # Compare results
        comparison = self._compare(primary_result, shadow_result)

        # Log comparison
        self._log_comparison(comparison, features)

        return comparison

    def _compare(
        self, primary: ModelResult, shadow: ModelResult | None
    ) -> ShadowComparison:
        """Compare primary and shadow results."""
        with tracer.start_as_current_span("shadow_comparison") as span:
            if shadow is None or not shadow.success:
                span.set_attribute("shadow_available", shadow is not None)
                return ShadowComparison(
                    primary=primary,
                    shadow=shadow,
                    predictions_agree=None,
                    latency_diff_ms=None,
                )

            predictions_agree = primary.prediction == shadow.prediction
            latency_diff_ms = shadow.latency_ms - primary.latency_ms

            span.set_attribute("predictions_agree", predictions_agree)
            span.set_attribute("latency_diff_ms", latency_diff_ms)

            if not predictions_agree:
                span.add_event(
                    "prediction_mismatch",
                    {
                        "primary_prediction": primary.prediction,
                        "shadow_prediction": shadow.prediction,
                    },
                )

            return ShadowComparison(
                primary=primary,
                shadow=shadow,
                predictions_agree=predictions_agree,
                latency_diff_ms=latency_diff_ms,
            )

    def _log_comparison(
        self, comparison: ShadowComparison, features: list[float]
    ) -> None:
        """Log comparison results for analysis."""
        if comparison.shadow is None:
            return

        extra_fields: dict[str, Any] = {
            "primary_version": comparison.primary.model_version,
            "primary_prediction": comparison.primary.prediction,
            "primary_probability": comparison.primary.probability,
            "primary_latency_ms": comparison.primary.latency_ms,
            "shadow_version": comparison.shadow.model_version,
            "shadow_success": comparison.shadow.success,
        }

        if comparison.shadow.success:
            extra_fields.update(
                {
                    "shadow_prediction": comparison.shadow.prediction,
                    "shadow_probability": comparison.shadow.probability,
                    "shadow_latency_ms": comparison.shadow.latency_ms,
                    "predictions_agree": comparison.predictions_agree,
                    "latency_diff_ms": comparison.latency_diff_ms,
                }
            )

            if not comparison.predictions_agree:
                extra_fields["features"] = features
                logger.warning(
                    "Shadow model prediction differs from primary",
                    extra={"extra_fields": extra_fields},
                )
            else:
                logger.debug(
                    "Shadow model comparison complete",
                    extra={"extra_fields": extra_fields},
                )
        else:
            extra_fields["shadow_error"] = comparison.shadow.error
            logger.warning(
                "Shadow model execution failed",
                extra={"extra_fields": extra_fields},
            )
