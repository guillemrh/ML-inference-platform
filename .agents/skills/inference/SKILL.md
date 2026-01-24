---
name: "ML Inference"
description: "Best practices for ML model serving, loading, latency optimization, and request/response schemas"
---

# ML Inference Skill

This skill covers ML inference patterns for production model serving.

## Topics

| Document | Description |
|----------|-------------|
| [model-loading.md](model-loading.md) | Model loading and versioning patterns |
| [latency.md](latency.md) | Latency optimization techniques |
| [schemas.md](schemas.md) | Request/response schema design |

## Core Principles

1. **Inference is not training** - No gradients, no learning rate, no training loops
2. **Load once, serve many** - Models loaded at startup, not per-request
3. **Fail fast, fail clear** - Validate inputs before inference
4. **Measure everything** - Latency, throughput, error rates

## Quick Reference

### Model Loading
- Load at application startup
- Singleton pattern for model instances
- Explicit version tracking

### Latency
- Target p99 < 100ms for simple models
- No I/O in hot path
- Batch when beneficial

### Schemas
- Explicit input/output contracts
- Include metadata in responses
- Version info always present
