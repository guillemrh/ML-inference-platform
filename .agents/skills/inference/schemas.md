# Request/Response Schemas

## Principles

1. **Explicit contracts** - Every field documented
2. **Validation at the edge** - Reject bad input early
3. **Rich responses** - Include metadata, not just predictions

## Request Schema

```python
from pydantic import BaseModel, Field, field_validator

class PredictRequest(BaseModel):
    """Request schema for /predict endpoint."""

    features: list[float] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Input features for the model"
    )

    model_version: str | None = Field(
        default=None,
        pattern=r"^v\d+\.\d+$",
        description="Specific model version (e.g., 'v1.0'). Uses default if not specified."
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: list[float]) -> list[float]:
        """Ensure features are valid numbers."""
        if any(not isinstance(x, (int, float)) for x in v):
            raise ValueError("All features must be numbers")
        if any(x != x for x in v):  # NaN check
            raise ValueError("Features cannot contain NaN")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "features": [1.0, 2.5, 3.0, 4.5],
                    "model_version": "v1.0"
                }
            ]
        }
    }
```

## Response Schema

```python
from pydantic import BaseModel, Field

class PredictResponse(BaseModel):
    """Response schema for /predict endpoint."""

    prediction: int = Field(
        ...,
        description="Model prediction (0 or 1 for binary classification)"
    )

    probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence probability for the prediction"
    )

    model_version: str = Field(
        ...,
        description="Version of the model used for this prediction"
    )

    latency_ms: float = Field(
        ...,
        ge=0.0,
        description="Inference latency in milliseconds"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prediction": 1,
                    "probability": 0.87,
                    "model_version": "v1.0",
                    "latency_ms": 12.5
                }
            ]
        }
    }
```

## Error Response Schema

```python
class ErrorDetail(BaseModel):
    """Detailed error information."""

    field: str | None = Field(
        default=None,
        description="Field that caused the error"
    )

    message: str = Field(
        ...,
        description="Human-readable error message"
    )

class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(
        ...,
        description="Error type"
    )

    detail: str | list[ErrorDetail] = Field(
        ...,
        description="Error details"
    )

    request_id: str | None = Field(
        default=None,
        description="Request correlation ID for debugging"
    )
```

## Schema Best Practices

### Use Descriptive Field Names

```python
# Good
class PredictRequest(BaseModel):
    features: list[float]
    model_version: str | None

# Bad
class PredictRequest(BaseModel):
    x: list[float]
    v: str | None
```

### Include Constraints

```python
features: list[float] = Field(
    ...,
    min_length=1,      # At least one feature
    max_length=100,    # Prevent huge payloads
)

probability: float = Field(
    ...,
    ge=0.0,            # Greater than or equal to 0
    le=1.0,            # Less than or equal to 1
)
```

### Provide Examples

```python
model_config = {
    "json_schema_extra": {
        "examples": [
            {"features": [1.0, 2.0, 3.0, 4.0]}
        ]
    }
}
```

### Document Everything

```python
features: list[float] = Field(
    ...,
    description="Input features for the model. Must match training feature count."
)
```

## HTTP Status Codes

| Status | When to Use |
|--------|-------------|
| 200 | Successful prediction |
| 400 | Bad request (malformed JSON) |
| 422 | Validation error (wrong types, constraints violated) |
| 500 | Internal error (model failure) |
| 503 | Model not ready (loading, unavailable) |

## Validation Error Response

FastAPI automatically generates this for Pydantic validation errors:

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "features"],
      "msg": "Features cannot contain NaN",
      "input": [1.0, "NaN", 3.0]
    }
  ]
}
```
