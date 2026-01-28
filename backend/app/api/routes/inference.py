"""
Inference API endpoint for Chemical Reactor Anomaly Detection.
"""

import time

from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.models import ModelNotLoadedError
from app.observability import record_prediction, record_shadow_result
from app.schemas import PredictRequest, PredictResponse
from app.services import ShadowRunner, get_model_manager

router = APIRouter()
logger = get_logger(__name__)


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    """
    Predict if reactor conditions indicate an anomaly.

    Takes reactor process parameters and returns a binary prediction
    indicating whether the current conditions are likely to produce
    off-spec product or trigger a safety event.

    If shadow mode is enabled, runs both primary and shadow models
    in parallel for comparison. Only the primary model's response
    is returned to the client.
    """
    start_time = time.perf_counter()

    model_manager = get_model_manager()
    primary = model_manager.primary

    if primary is None or not primary.is_loaded:
        logger.error("Prediction attempted but model not loaded")
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Service is starting up.",
        )

    # Extract features in the expected order
    features = [
        request.temperature,
        request.pressure,
        request.flow_rate,
        request.reactant_concentration,
        request.ph_level,
        request.stirrer_speed,
    ]

    try:
        if model_manager.shadow_enabled:
            # Run with shadow mode
            shadow_runner = ShadowRunner(
                primary_model=primary,
                shadow_model=model_manager.shadow,
            )
            comparison = await shadow_runner.run(features)
            result = comparison.primary

            # Record shadow metrics
            if comparison.shadow is not None:
                if comparison.shadow.success:
                    record_shadow_result(
                        status="success",
                        duration_seconds=comparison.shadow.latency_ms / 1000,
                        agreed=comparison.predictions_agree,
                        latency_diff_seconds=comparison.latency_diff_ms / 1000
                        if comparison.latency_diff_ms
                        else None,
                    )
                elif comparison.shadow.error and "timed out" in comparison.shadow.error:
                    record_shadow_result(status="timeout")
                else:
                    record_shadow_result(status="error")

            if not result.success:
                raise Exception(result.error)

            latency_ms = result.latency_ms
            model_version = result.model_version
            prediction_result = {
                "prediction": result.prediction,
                "probability": result.probability,
                "label": result.label,
            }
        else:
            # Run without shadow mode (direct model call)
            prediction_result = primary.predict(features)
            latency_ms = (time.perf_counter() - start_time) * 1000
            model_version = primary.version

    except ModelNotLoadedError:
        raise HTTPException(status_code=503, detail="Model not available")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(
            "Inference failed",
            extra={"extra_fields": {"error": str(e)}},
        )
        raise HTTPException(status_code=500, detail="Inference failed")

    # Record primary model metrics
    latency_seconds = latency_ms / 1000
    record_prediction(label=prediction_result["label"], duration_seconds=latency_seconds)

    logger.info(
        "Prediction completed",
        extra={
            "extra_fields": {
                "prediction": prediction_result["prediction"],
                "probability": prediction_result["probability"],
                "model_version": model_version,
                "latency_ms": round(latency_ms, 2),
                "shadow_enabled": model_manager.shadow_enabled,
            }
        },
    )

    return PredictResponse(
        prediction=prediction_result["prediction"],
        probability=prediction_result["probability"],
        label=prediction_result["label"],
        model_version=model_version,
        latency_ms=round(latency_ms, 2),
    )
