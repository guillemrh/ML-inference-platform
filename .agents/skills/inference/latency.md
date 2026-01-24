# Latency Optimization

## Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| p50 | < 20ms | < 50ms |
| p95 | < 50ms | < 100ms |
| p99 | < 100ms | < 200ms |

## Measurement

### Response Metadata

Always include latency in responses:

```python
import time
from pydantic import BaseModel

class InferenceResponse(BaseModel):
    prediction: float
    model_version: str
    latency_ms: float

@router.post("/predict")
async def predict(request: PredictRequest) -> InferenceResponse:
    start = time.perf_counter()

    # Inference
    result = model.predict(request.features)

    latency_ms = (time.perf_counter() - start) * 1000

    return InferenceResponse(
        prediction=result,
        model_version=loader.version,
        latency_ms=round(latency_ms, 2)
    )
```

### Prometheus Metrics

```python
from prometheus_client import Histogram

INFERENCE_LATENCY = Histogram(
    "inference_latency_seconds",
    "Inference latency in seconds",
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

@router.post("/predict")
async def predict(request: PredictRequest):
    with INFERENCE_LATENCY.time():
        result = model.predict(request.features)
    return {"prediction": result}
```

## Optimization Techniques

### 1. Avoid I/O in Hot Path

```python
# BAD - file I/O during inference
def predict(features):
    config = json.load(open("config.json"))  # Slow!
    return model.predict(features)

# GOOD - config loaded at startup
config = json.load(open("config.json"))  # Once

def predict(features):
    return model.predict(features)
```

### 2. Minimize Data Copies

```python
import numpy as np

# BAD - multiple copies
def preprocess(data: list[float]) -> np.ndarray:
    arr = np.array(data)      # Copy 1
    arr = arr.reshape(1, -1)  # Copy 2
    arr = arr.astype(float)   # Copy 3
    return arr

# GOOD - single allocation
def preprocess(data: list[float]) -> np.ndarray:
    return np.array(data, dtype=np.float32).reshape(1, -1)
```

### 3. Use Appropriate Data Types

```python
# float32 is often sufficient and faster than float64
features = np.array(data, dtype=np.float32)
```

### 4. Batch When Beneficial

```python
# Single predictions are fine for low throughput
# For high throughput, batch multiple requests

async def batch_predict(requests: list[PredictRequest]):
    # Combine into single batch
    batch = np.vstack([r.features for r in requests])

    # Single model call
    predictions = model.predict(batch)

    return predictions.tolist()
```

### 5. Model Optimization (scikit-learn)

```python
# Use joblib with compression for smaller files
import joblib

# Save with compression
joblib.dump(model, "model.pkl", compress=3)

# For sklearn, n_jobs=-1 uses all cores (if model supports)
model = RandomForestClassifier(n_jobs=-1)
```

## Profiling

### Simple Timing

```python
import time

def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}: {elapsed*1000:.2f}ms")
        return result
    return wrapper

@timed
def predict(features):
    return model.predict(features)
```

### Breakdown Timing

```python
def predict_with_breakdown(features):
    times = {}

    t0 = time.perf_counter()
    processed = preprocess(features)
    times["preprocess"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    result = model.predict(processed)
    times["inference"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    response = format_response(result)
    times["postprocess"] = time.perf_counter() - t0

    logger.info("Timing breakdown", extra={"extra_fields": times})
    return response
```

## Common Latency Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Model reloading | High p99, spikes | Load at startup |
| Disk I/O | Inconsistent latency | Cache/preload |
| Large payloads | Slow all requests | Validate size limits |
| GC pauses | Random spikes | Tune GC, reduce allocations |
