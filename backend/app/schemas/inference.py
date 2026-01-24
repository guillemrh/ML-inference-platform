"""
Request/response schemas for inference endpoint.
"""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Request schema for /predict endpoint."""

    temperature: float = Field(
        ...,
        ge=0,
        le=200,
        description="Reactor temperature in Celsius (typical: 60-120)",
    )
    pressure: float = Field(
        ...,
        ge=0,
        le=20,
        description="Vessel pressure in bar (typical: 1-10)",
    )
    flow_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Feed flow rate in L/min (typical: 5-50)",
    )
    reactant_concentration: float = Field(
        ...,
        ge=0,
        le=5,
        description="Reactant concentration in mol/L (typical: 0.5-2.0)",
    )
    ph_level: float = Field(
        ...,
        ge=0,
        le=14,
        description="pH of mixture (typical: 4-10)",
    )
    stirrer_speed: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Agitator speed in RPM (typical: 100-500)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "temperature": 85.0,
                    "pressure": 5.5,
                    "flow_rate": 25.0,
                    "reactant_concentration": 1.2,
                    "ph_level": 7.0,
                    "stirrer_speed": 300.0,
                }
            ]
        }
    }


class PredictResponse(BaseModel):
    """Response schema for /predict endpoint."""

    prediction: int = Field(
        ...,
        ge=0,
        le=1,
        description="Binary prediction (0=normal, 1=anomaly)",
    )
    probability: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence probability for the prediction",
    )
    label: str = Field(
        ...,
        description="Human-readable label ('normal' or 'anomaly')",
    )
    model_version: str = Field(
        ...,
        description="Version of the model used for prediction",
    )
    latency_ms: float = Field(
        ...,
        ge=0,
        description="Inference latency in milliseconds",
    )

    model_config = {
        "protected_namespaces": (),  # Allow model_ prefix in field names
        "json_schema_extra": {
            "examples": [
                {
                    "prediction": 0,
                    "probability": 0.85,
                    "label": "normal",
                    "model_version": "v1",
                    "latency_ms": 2.5,
                }
            ]
        },
    }
