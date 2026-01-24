# Model Loading

## Principles

1. **Load once at startup** - Never reload per-request
2. **Explicit versioning** - Know exactly which model is serving
3. **Graceful degradation** - Handle missing models cleanly

## Loading Patterns

### Singleton Pattern (Recommended)

```python
from pathlib import Path
from functools import lru_cache
import joblib

class ModelLoader:
    """Singleton model loader."""

    _instance: "ModelLoader | None" = None
    _model = None
    _version: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, model_path: Path, version: str) -> None:
        """Load model from disk."""
        self._model = joblib.load(model_path)
        self._version = version

    @property
    def model(self):
        if self._model is None:
            raise RuntimeError("Model not loaded")
        return self._model

    @property
    def version(self) -> str:
        return self._version


# Usage
loader = ModelLoader()
loader.load(Path("models/classifier_v1.pkl"), "v1.0")
```

### Application Lifespan Loading

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model
    loader = ModelLoader()
    loader.load(
        Path(settings.model_path),
        version=settings.model_version
    )
    logger.info(f"Model loaded: {loader.version}")

    yield

    # Shutdown: Cleanup if needed
    logger.info("Application shutting down")
```

## Versioning

### File-Based Versioning

```
models/
├── classifier_v1.0.pkl
├── classifier_v1.1.pkl
└── classifier_v2.0.pkl
```

### Configuration-Based

```python
# config.py
class Settings(BaseSettings):
    model_version: str = "v1.0"
    model_dir: Path = Path("models")

    @property
    def model_path(self) -> Path:
        return self.model_dir / f"classifier_{self.model_version}.pkl"
```

## Error Handling

```python
class ModelNotFoundError(Exception):
    """Raised when model file doesn't exist."""
    pass

class ModelLoadError(Exception):
    """Raised when model fails to load."""
    pass

def load_model(path: Path) -> Model:
    """Load model with proper error handling."""
    if not path.exists():
        raise ModelNotFoundError(f"Model not found: {path}")

    try:
        return joblib.load(path)
    except Exception as e:
        raise ModelLoadError(f"Failed to load model: {e}") from e
```

## Health Check Integration

```python
@router.get("/health")
async def health():
    """Health check with model status."""
    try:
        loader = ModelLoader()
        model_ready = loader.model is not None
        version = loader.version
    except RuntimeError:
        model_ready = False
        version = None

    return {
        "status": "healthy" if model_ready else "degraded",
        "model_loaded": model_ready,
        "model_version": version
    }
```

## Anti-Patterns

### Don't: Load per request

```python
# BAD - loads model on every request
@router.post("/predict")
async def predict(request: PredictRequest):
    model = joblib.load("model.pkl")  # Wrong!
    return model.predict(request.features)
```

### Don't: Ignore version

```python
# BAD - no version tracking
model = joblib.load("model.pkl")  # Which version?
```

### Don't: Silent failures

```python
# BAD - silently returns None
def load_model(path):
    try:
        return joblib.load(path)
    except:
        return None  # Caller won't know why
```
