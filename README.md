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
## Project Structure
```
ml-inference-platform/
│
├── CLAUDE.md                       # Claude Code project context
├── .claude/                        # Claude Code configuration
│   ├── settings.json
│   └── commands/                   # Slash commands (/test, /lint, etc.)
│
├── .agents/                        # AI agents and skills
│   ├── agents/                     # Subagent definitions
│   │   ├── model-reviewer.md       # Reviews ML model code
│   │   └── api-reviewer.md         # Reviews API code
│   └── skills/                     # Best practices documentation
│       ├── coding/                 # Python standards, testing
│       ├── inference/              # ML inference patterns
│       └── workflows/              # Docker, PR workflow
│
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
│   │   ├── observability/
│   │   │    ├── __init__.py
│   │   │    ├── metrics.py           # Prometheus metrics
│   │   │    └── health.py            # internal health checks
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

## AI-Assisted Development

This project uses Claude Code for AI-assisted development with:

### Commands
| Command | Description |
|---------|-------------|
| `/test` | Run pytest in Docker container |
| `/lint` | Run ruff linter and formatter |
| `/add-endpoint` | Scaffold a new API endpoint |

### Subagents
| Agent | Model | Purpose |
|-------|-------|---------|
| `model-reviewer` | opus | Reviews ML model code for inference best practices |
| `api-reviewer` | sonnet | Reviews API code for production readiness |

### Skills
Best practices documentation organized by domain:
- **coding/** - Python standards, testing patterns
- **inference/** - Model loading, latency, schemas
- **workflows/** - Docker, PR workflow

See [CLAUDE.md](CLAUDE.md) for full project context and [.agents/](.agents/) for agent/skill details.

---

## Technology Stack

- **Language:** Python
- **API:** FastAPI
- **ML Runtime:** Lightweight Python model wrappers
- **Metrics:** Prometheus-compatible
- **Containers:** Docker + docker-compose
- **Testing:** pytest
- **AI Assistance:** Claude Code

---

## Project Status

### Completed
- [x] Architecture defined
- [x] Project structure finalized
- [x] Inference API implemented (`POST /predict`, `GET /health`)
- [x] Basic observability (Prometheus metrics, Grafana dashboards)
- [x] CI pipeline (GitHub Actions)
- [x] Docker-first development workflow

### In Progress
- [ ] Model versioning (explicit version tracking in responses)

### Planned
- [ ] Shadow mode (challenger model pattern)
- [ ] Canary deployments (gradual traffic shifting)
- [ ] Distributed tracing (OpenTelemetry + Jaeger)
- [ ] Model registry service

---

## Development Roadmap

This roadmap is designed to progressively answer the hard questions from "Why This Project Exists" while building production-grade ML infrastructure skills.

---

### Stage 1: Shadow Mode (Challenger Pattern)

**Status:** Next up

**What it is:**
Run a "shadow" model alongside the primary model. Both receive the same input, but only the primary model's prediction is returned to the user. The shadow model's prediction is logged for comparison.

```
Request → API → ┬→ Primary Model (v1) → Response to user
                └→ Shadow Model (v2) → Log only (no user impact)
                         ↓
                  Compare: latency, predictions, errors
```

**Why it matters:**
- Test new models in production with **zero risk** to users
- Compare model behavior on **real traffic**, not just test data
- Catch regressions before they affect users
- Build confidence before promoting a new model

**What you'll learn:**
- Parallel execution patterns in async Python
- Comparing model outputs systematically
- Observability for model comparison (metrics, logs)
- Decision criteria for model promotion

**Key components to build:**
| Component | Purpose |
|-----------|---------|
| `ShadowRunner` | Executes shadow model in parallel, handles timeouts |
| `ComparisonLogger` | Logs primary vs shadow predictions for analysis |
| Shadow metrics | `shadow_model_latency`, `prediction_agreement_rate` |
| Configuration | Enable/disable shadow mode, select shadow model version |

**Success criteria:**
- Shadow model runs on every request without affecting response latency significantly (<10% overhead)
- Can compare predictions between primary and shadow in Grafana
- Shadow failures don't break primary responses

---

### Stage 2: Canary Deployments

**Status:** After shadow mode

**What it is:**
Gradually shift traffic from the old model to the new model. Start with 1%, monitor, increase to 10%, monitor, then 100%.

```
Request → Traffic Router → ┬→ 90% → Model v1 (stable)
                           └→ 10% → Model v2 (canary)
```

**Why it matters:**
- Shadow mode proves the model *can* work; canary proves it *does* work for real users
- Limit blast radius: if v2 is broken, only 10% of users are affected
- Gradual rollout with rollback capability
- This is how Netflix, Google, Uber deploy ML models

**What you'll learn:**
- Traffic splitting strategies (random, user-based, feature-based)
- Rollback mechanisms and triggers
- Deployment automation patterns
- Statistical significance in A/B comparisons

**Key components to build:**
| Component | Purpose |
|-----------|---------|
| `TrafficRouter` | Routes requests based on configured weights |
| Rollout configuration | Define traffic split percentages |
| Rollback triggers | Auto-rollback on error rate spike |
| Canary metrics | Per-version latency, error rate, prediction distribution |

**Progression:**
1. Manual traffic splitting (config change)
2. API-driven traffic control (`POST /admin/traffic-split`)
3. Automated rollback on anomaly detection (stretch goal)

**Success criteria:**
- Can route X% of traffic to canary model via configuration
- Grafana shows per-model-version metrics side by side
- Can rollback to 0% canary traffic quickly

---

### Stage 3: Distributed Tracing (OpenTelemetry + Jaeger)

**Status:** After canary deployments

**What it is:**
Instrument the system to trace individual requests across all components. Each request gets a trace ID that follows it through the entire flow.

```
Trace: abc-123
├─ API Gateway (5ms)
├─ Traffic Router (1ms)
├─ Model v2 - Canary (150ms)
│   ├─ Input validation (2ms)
│   ├─ Feature preparation (8ms)
│   └─ Inference (140ms)
└─ Response formatting (2ms)
```

**Why it matters:**
- With shadow mode and canary, you now have **multiple paths** through the system
- "Why was this specific request slow?" requires tracing, not just metrics
- Debug production issues without guessing
- Understand where latency actually comes from

**What you'll learn:**
- OpenTelemetry instrumentation (spans, context propagation)
- Trace collection and visualization (Jaeger)
- Correlation between traces, metrics, and logs
- Performance profiling in production

**Key components to build:**
| Component | Purpose |
|-----------|---------|
| OpenTelemetry SDK | Instrument FastAPI, model inference |
| Jaeger | Collect and visualize traces |
| Custom spans | Model loading, inference, shadow execution |
| Trace-metric correlation | Link trace IDs to Prometheus metrics |

**Success criteria:**
- Every request has a trace visible in Jaeger
- Can see shadow model execution as a parallel span
- Can filter traces by model version, latency, error status

---

### Stage 4: Model Registry Service (Future)

**Status:** Future consideration

**What it is:**
A separate service that manages model artifacts, versions, and metadata. The inference service queries the registry to know which models to load.

```
Inference Service → Model Registry → "What's the current primary model?"
                          ↓
                  Returns: model_path, version, config
                          ↓
                  Inference Service loads and caches model
```

**Why it matters:**
- Decouples model management from inference
- Enables dynamic model loading without redeployment
- Central source of truth for model versions
- Foundation for more advanced patterns (A/B tests, multi-armed bandits)

**What you'll learn:**
- Service-to-service communication patterns
- Model artifact storage and retrieval
- Cache invalidation strategies
- API design for internal services

**Key components to build:**
| Component | Purpose |
|-----------|---------|
| Registry API | `GET /models/{name}/active`, `POST /models/{name}/promote` |
| Model storage | Store model artifacts (local filesystem → S3 later) |
| Metadata DB | Track versions, promotion history, rollback points |
| Cache layer | Inference service caches loaded models |

**Success criteria:**
- Can promote a new model version via API without redeploying inference service
- Inference service automatically picks up new model versions
- Full audit trail of model promotions

---

### Roadmap Summary

| Stage | Focus | Key Question Answered |
|-------|-------|----------------------|
| 1. Shadow Mode | Safe comparison | "Is the new model behaving correctly?" |
| 2. Canary | Safe rollout | "Does the new model work for real users?" |
| 3. Tracing | Debuggability | "Why was this specific request slow/broken?" |
| 4. Registry | Dynamic management | "How do we manage models without redeploying?" |

Each stage builds on the previous. Shadow mode is prerequisite for canary (you should shadow first). Tracing becomes valuable once you have multiple code paths (shadow + canary). Registry is optional but enables more sophisticated patterns.

---

## Guiding Principle

> Treat ML inference as **backend engineering with math inside**, not magic.

Clarity, correctness, and operability come first.
