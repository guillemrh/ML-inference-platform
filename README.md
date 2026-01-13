# ML Inference Platform

A **production-oriented ML inference system** focused on correctness, latency, observability, and operational clarity.

This project is intentionally **not about training models**.
It is about **serving ML models as real software systems**.

---

## Why This Project Exists

Most ML demos stop at:
> “Here’s a trained model and an endpoint.”

Real systems must answer harder questions:
- How do we version models safely?
- How do we measure latency and failures?
- What happens when a model is slow or broken?
- How do we roll out changes without breaking users?

This project exists to **practice ML systems engineering**, not data science.

---

## Core Objectives

This platform is designed to practice and demonstrate:

- Production-style ML inference APIs
- Explicit request / response contracts
- Explicit model versioning (single active version)
- Latency-aware system design
- Observability (metrics, logs, health checks)
- Dockerized, deployable architecture
- Clean separation of concerns

---

## Non-Goals (Very Important)

To keep the scope realistic and focused, this project intentionally does **not** include:

- Model training pipelines
- AutoML or hyperparameter tuning
- Complex orchestration frameworks
- UI-heavy dashboards
- Distributed training

Those are separate problems.

---

## High-Level Architecture

At a minimum, the system consists of:

- **Inference API**  
  Receives prediction requests, validates input, routes to a model, and returns results.

- **Model Runtime**  
  Loads one or more model versions and performs inference.

- **Observability Layer**  
  Exposes health, metrics, and structured logs.

- **Configuration Layer**  
  Controls model versions, routing rules, and runtime behavior.

All components run in Docker containers and communicate over a private Docker network.

---

## Example Request Flow

1. Client sends a prediction request
2. API validates schema
3. Request is routed to a specific model version
4. Model performs inference
5. Response is returned with metadata (model version, latency)
6. Metrics and logs are emitted

---
## Project structure
```
ml-inference-platform/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   └── inference.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── neural_net.py
│   │   │   └── loader.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── inference.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── inference_service.py
│   │   └── utils/
│   │       └── __init__.py
│   ├── tests/
│   │   ├── test_health.py
│   │   └── test_inference.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── README.md
└── .gitignore

```
---

## API Design (Initial)

### POST /predict

Input:
- Structured JSON payload
- Explicit schema validation

Output:
- Prediction result
- Model version used
- Inference latency

---

### GET /health

- Used by orchestrators and load balancers
- Must be fast and deterministic
- No heavy dependencies

---

### GET /metrics

- Prometheus-compatible metrics
- Request count
- Error count
- Latency buckets

---

## Testing Strategy

This project includes testing at multiple levels:

- **Unit tests**
  - Request validation
  - Routing logic
  - Model wrapper behavior

- **Integration tests**
  - End-to-end inference call
  - Health check behavior

Tests are designed to be:
- Fast
- Deterministic
- Runnable in CI

---

## Observability Principles

- Structured logs (JSON)
- Explicit correlation fields
- Clear separation between:
  - application errors
  - model errors
  - infrastructure errors

Metrics focus on:
- Request rate
- Error rate
- Latency (p50 / p95 / p99)

---

## Technology Stack

- **Language:** Python
- **API:** FastAPI
- **ML Runtime:** Lightweight Python model wrappers
- **Metrics:** Prometheus-compatible
- **Containers:** Docker + docker-compose
- **Testing:** pytest

---

## Project Status

- [ ] Architecture defined
- [ ] Project structure finalized
- [ ] Inference API implemented
- [ ] Model versioning implemented
- [ ] Observability added
- [ ] CI pipeline added

This checklist is intentionally incremental.

---

## Guiding Principle

> Treat ML inference as **backend engineering with math inside**, not magic.

Clarity, correctness, and operability come first.
