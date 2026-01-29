"""
Inference API endpoint for Chemical Reactor Anomaly Detection.
"""

import time

from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.models import ModelNotLoadedError
from app.observability import (
    get_tracer,
    record_canary_routing,
    record_prediction,
    record_shadow_result,
)
from app.schemas import PredictRequest, PredictResponse
from app.services import ShadowRunner, get_model_manager

router = APIRouter()
logger = get_logger(__name__)
tracer = get_tracer(__name__)


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
    with tracer.start_as_current_span("extract_features") as span:
        features = [
            request.temperature,
            request.pressure,
            request.flow_rate,
            request.reactant_concentration,
            request.ph_level,
            request.stirrer_speed,
        ]
        span.set_attribute("feature_count", len(features))

    try:
        if model_manager.canary_enabled:
            with tracer.start_as_current_span("canary_routing") as span:
                # Canary mode: route to one model based on traffic weight
                traffic_router = model_manager.traffic_router
                use_canary = traffic_router.should_route_to_canary()
                chosen_model = model_manager.secondary if use_canary else primary
                routed_to = "canary" if use_canary else "primary"

                span.set_attribute("deployment_mode", "canary")
                span.set_attribute("routed_to", routed_to)
                span.set_attribute("canary_weight", traffic_router.canary_weight)

                with tracer.start_as_current_span("model.predict") as inf_span:
                    inf_span.set_attribute("model_name", routed_to)
                    inf_span.set_attribute("model_version", chosen_model.version)
                    prediction_result = chosen_model.predict(features)
                    inf_span.set_attribute(
                        "prediction", prediction_result["prediction"]
                    )

                latency_ms = (time.perf_counter() - start_time) * 1000
                model_version = chosen_model.version

                record_canary_routing(routed_to)

        elif model_manager.shadow_enabled:
            with tracer.start_as_current_span("shadow_execution") as span:
                span.set_attribute("deployment_mode", "shadow")
                # Shadow mode: run both, return primary
                shadow_runner = ShadowRunner(
                    primary_model=primary,
                    shadow_model=model_manager.secondary,
                )
                comparison = await shadow_runner.run(features)
                result = comparison.primary

                # Record shadow metrics
                if comparison.shadow is not None:
                    span.set_attribute("shadow_success", comparison.shadow.success)
                    if comparison.predictions_agree is not None:
                        span.set_attribute(
                            "predictions_agree", comparison.predictions_agree
                        )
                    if comparison.shadow.success:
                        record_shadow_result(
                            status="success",
                            duration_seconds=comparison.shadow.latency_ms / 1000,
                            agreed=comparison.predictions_agree,
                            latency_diff_seconds=(
                                comparison.latency_diff_ms / 1000
                                if comparison.latency_diff_ms
                                else None
                            ),
                        )
                    elif (
                        comparison.shadow.error
                        and "timed out" in comparison.shadow.error
                    ):
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
            with tracer.start_as_current_span("direct_inference") as span:
                span.set_attribute("deployment_mode", "direct")

                with tracer.start_as_current_span("model.predict") as inf_span:
                    inf_span.set_attribute("model_name", "primary")
                    inf_span.set_attribute("model_version", primary.version)
                    prediction_result = primary.predict(features)
                    inf_span.set_attribute(
                        "prediction", prediction_result["prediction"]
                    )

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

    # Record model metrics
    latency_seconds = latency_ms / 1000
    record_prediction(
        label=prediction_result["label"],
        duration_seconds=latency_seconds,
        model_version=model_version,
    )

    logger.info(
        "Prediction completed",
        extra={
            "extra_fields": {
                "prediction": prediction_result["prediction"],
                "probability": prediction_result["probability"],
                "model_version": model_version,
                "latency_ms": round(latency_ms, 2),
                "deployment_mode": model_manager.deployment_mode,
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
