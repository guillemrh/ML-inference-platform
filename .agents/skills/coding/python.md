# Python Standards

## Language Version

- **Python 3.11+** is required
- Use modern Python features where they improve clarity

## Type Hints

Type hints are **required** on all function signatures.

```python
# Good
def predict(input_data: list[float]) -> dict[str, float]:
    ...

# Bad
def predict(input_data):
    ...
```

### Common Patterns

```python
from typing import Optional

# Optional parameters
def load_model(version: str, cache: bool = True) -> Model:
    ...

# Return type with Optional
def get_model(name: str) -> Optional[Model]:
    ...

# Using | for union types (Python 3.10+)
def process(data: str | bytes) -> dict:
    ...
```

## Pydantic Models

Use Pydantic for all data validation, especially API schemas.

```python
from pydantic import BaseModel, Field

class InferenceRequest(BaseModel):
    """Request schema for inference endpoint."""

    features: list[float] = Field(
        ...,
        min_length=1,
        description="Input features for the model"
    )
    model_version: str | None = Field(
        default=None,
        description="Specific model version to use"
    )
```

## Exception Handling

### Do
```python
try:
    result = model.predict(data)
except ModelNotLoadedError:
    raise HTTPException(status_code=503, detail="Model not ready")
except InvalidInputError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

### Don't
```python
# Never use bare except
try:
    result = model.predict(data)
except:  # Bad!
    pass
```

## Imports

Organize imports in this order:
1. Standard library
2. Third-party packages
3. Local imports

```python
# Standard library
import os
from pathlib import Path

# Third-party
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Local
from app.core.config import settings
from app.models.loader import load_model
```

## Logging

Use structured logging via the project's logging module.

```python
from app.core.logging import get_logger

logger = get_logger(__name__)

# Include context in extra_fields
logger.info(
    "Inference completed",
    extra={
        "extra_fields": {
            "model_version": "v1.0",
            "latency_ms": 45.2,
            "request_id": request_id
        }
    }
)
```

## Docstrings

Use docstrings for public functions and classes.

```python
def load_model(path: Path, version: str) -> Model:
    """
    Load a model from disk.

    Args:
        path: Path to model directory
        version: Specific version to load

    Returns:
        Loaded model instance

    Raises:
        ModelNotFoundError: If model version doesn't exist
    """
```

## Constants

Use UPPER_CASE for constants, define at module level.

```python
DEFAULT_MODEL_VERSION = "v1.0"
MAX_BATCH_SIZE = 32
INFERENCE_TIMEOUT_SECONDS = 30
```
