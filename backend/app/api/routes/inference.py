"""
Inference API endpoint for Chemical Reactor Anomaly Detection.
"""

import time

from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.models import ModelNotLoadedError, get_model
from app.observability import record_prediction
from app.schemas import PredictRequest, PredictResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest) -> PredictResponse:
    """
    Predict if reactor conditions indicate an anomaly.

    Takes reactor process parameters and returns a binary prediction
    indicating whether the current conditions are likely to produce
    off-spec product or trigger a safety event.
    """
    start_time = time.perf_counter()

    model = get_model()

    if not model.is_loaded:
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
        result = model.predict(features)
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

    latency_seconds = time.perf_counter() - start_time
    latency_ms = latency_seconds * 1000

    # Record metrics
    record_prediction(label=result["label"], duration_seconds=latency_seconds)

    logger.info(
        "Prediction completed",
        extra={
            "extra_fields": {
                "prediction": result["prediction"],
                "probability": result["probability"],
                "model_version": model.version,
                "latency_ms": round(latency_ms, 2),
            }
        },
    )

    return PredictResponse(
        prediction=result["prediction"],
        probability=result["probability"],
        label=result["label"],
        model_version=model.version,
        latency_ms=round(latency_ms, 2),
    )
