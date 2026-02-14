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
│   │   ├── model-reviewer.md
│   │   └── api-reviewer.md
│   └── skills/                     # Best practices documentation
│       ├── coding/                 # Python standards, testing
│       ├── inference/              # ML inference patterns
│       └── workflows/              # Docker, PR workflow
│
├── backend/                        # Main inference service
│   ├── app/
│   │   ├── main.py                 # FastAPI entrypoint
│   │   ├── api/routes/
│   │   │   ├── health.py           # Health check endpoint
│   │   │   ├── inference.py        # POST /predict endpoint
│   │   │   └── admin.py            # Traffic control endpoints
│   │   ├── clients/
│   │   │   └── registry_client.py  # Model registry client
│   │   ├── core/
│   │   │   ├── config.py           # Environment settings
│   │   │   └── logging.py          # Structured JSON logging
│   │   ├── models/
│   │   │   └── loader.py           # Model loading utilities
│   │   ├── schemas/
│   │   │   └── inference.py        # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── model_manager.py    # Model lifecycle management
│   │   │   ├── shadow_runner.py    # Shadow mode execution
│   │   │   └── traffic_router.py   # Canary traffic routing
│   │   └── observability/
│   │       ├── metrics.py          # Prometheus metrics
│   │       ├── middleware.py       # Request metrics middleware
│   │       └── tracing.py          # OpenTelemetry instrumentation
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_inference.py
│   │   ├── test_shadow_mode.py
│   │   ├── test_canary_mode.py
│   │   ├── test_tracing.py
│   │   ├── test_metrics.py
│   │   └── test_registry_client.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── registry/                       # Model registry microservice
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/
│   │   │   ├── health.py
│   │   │   └── models.py           # Registry CRUD endpoints
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging.py
│   │   ├── db/
│   │   │   ├── database.py         # SQLAlchemy setup
│   │   │   └── models.py           # ORM models
│   │   ├── schemas/
│   │   │   └── models.py           # Pydantic schemas
│   │   └── services/
│   │       └── registry.py         # Registry business logic
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   └── test_models_api.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── models/                         # Model training scripts
│   ├── train_reactor_model.py      # v1 LogisticRegression
│   └── train_reactor_model_v2.py   # v2 RandomForest
│
├── monitoring/                     # Observability infrastructure
│   ├── prometheus.yml              # Prometheus scrape config
│   ├── loki/
│   │   └── loki-config.yml         # Loki storage/retention config
│   ├── promtail/
│   │   └── promtail-config.yml     # Docker log shipping config
│   └── grafana/provisioning/
│       ├── datasources/
│       │   ├── prometheus.yml
│       │   └── loki.yml            # Loki + Jaeger trace linking
│       └── dashboards/
│           ├── dashboards.yml
│           ├── ml-inference.json   # Metrics dashboard
│           └── logs.json           # Logs dashboard
│
├── scripts/
│   └── load_generator.py           # Traffic generation for testing
│
├── docker-compose.yml              # Full stack orchestration
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

### Stage 1: Shadow Mode (Challenger Pattern)
- [x] ShadowRunner service (parallel execution, timeout handling)
- [x] ModelManager (primary + shadow lifecycle)
- [x] Shadow metrics (agreement rate, latency diff, error/timeout counters)
- [x] Configuration (env-based toggle, model paths, timeout)
- [x] Tests (39 passing — unit, integration, shadow-specific)
- [x] E2E validation with identical model — 100% agreement, infrastructure confirmed working
- [x] E2E validation with real challenger (RandomForest v2 vs LogisticRegression v1):
  <!-- 500 requests, 100% HTTP success. 99.6% prediction agreement (2 edge-case divergences).
       v2 latency 85x slower (25.5ms avg vs 0.3ms) — blocker for promotion.
       Shadow mode correctly surfaced the latency regression before any user impact. -->

### Stage 2: Canary Deployments
- [x] TrafficRouter (weight-based request routing)
- [x] Rollout configuration (traffic split percentages)
- [x] Per-version metrics (latency, error rate, prediction distribution)
- [ ] Rollback triggers (auto-rollback on error spike) — stretch goal
- [x] API-driven traffic control (`POST /admin/traffic-split`)
- [x] E2E validation: 10% → 50% → 0% rollback, all routing correct
  <!-- 1200 requests total. At 10%: 453 primary / 47 canary (9.4%).
       Runtime change to 50%: split matched immediately. Rollback to 0%:
       zero canary traffic instantly. v2 avg latency 2.98ms vs v1 0.15ms (20x slower).
       Promotion decision: NO — latency regression confirmed. -->

### Stage 3: Distributed Tracing (OpenTelemetry + Jaeger)
- [x] OpenTelemetry SDK instrumentation (FastAPI, model inference)
- [x] Jaeger trace collection and visualization
- [x] Custom spans (model loading, inference, shadow execution, canary routing)
- [x] Trace-log correlation (trace_id/span_id injected into structured JSON logs)
- [x] Configurable sampling rate (`TRACE_SAMPLE_RATE` env var)
- [x] Tests (64 passing)

### Stage 4: Model Registry Service
- [x] Separate FastAPI microservice (`registry/`) with PostgreSQL
- [x] Registry API (register, list, promote, rollback, active query, history)
- [x] Metadata DB (SQLAlchemy ORM — models, model_history, active_deployments)
- [x] Backend registry client with feature-flag toggle (`REGISTRY_ENABLED`)
- [x] Startup-only discovery with env var fallback
- [x] Tests (15 registry + 5 backend client, all passing)

### Stage 5: Centralized Logging (Grafana Loki)
- [x] Loki log aggregation service (filesystem storage, 7-day retention)
- [x] Promtail log shipper (Docker service discovery, JSON parsing)
- [x] Grafana Loki datasource with Jaeger trace-log correlation (derived fields)
- [x] Pre-built logs dashboard (log volume, errors, per-service breakdown, live tail)
- [x] E2E verification: trace_id queryable in Loki from prediction requests
- [x] No application code changes — pure infrastructure integration

---

## Stage Results

**Stage 1 — Shadow Mode:** Ran 500 requests with RandomForest v2 shadowing LogisticRegression v1. 99.6% prediction agreement (2 edge-case divergences), but v2 was 85x slower (25.5ms vs 0.3ms) — shadow mode correctly surfaced the latency regression before any user impact. Promotion decision: **no**.

**Stage 2 — Canary Deployments:** Ran 1200 requests across three phases (10% → 50% → 0% rollback). Traffic routing matched configured weights at every step, and runtime weight changes via `POST /admin/traffic-split` took effect instantly without restart. v2 confirmed 20x slower (2.98ms vs 0.15ms). Promotion decision: **no** — same latency regression, now validated with real user-facing traffic.

**Stage 3 — Distributed Tracing:** Added OpenTelemetry instrumentation with Jaeger. Every request now produces a full trace with spans for feature extraction, routing decisions, and model inference — trace IDs are injected into structured logs for correlation. Jaeger UI at `localhost:16687` shows the complete span hierarchy per request.

**Stage 4 — Model Registry:** Separate FastAPI microservice with PostgreSQL for model metadata, versioning, and lifecycle management. Register models, promote to active, rollback to previous versions — all via API with full audit trail. Backend queries registry at startup to discover active models, with automatic fallback to env vars when registry is disabled or unreachable. Promote/rollback tested end-to-end.

**Stage 5 — Centralized Logging:** Added Grafana Loki + Promtail to complete the three pillars of observability (metrics, traces, logs). Promtail discovers all Docker containers via socket and ships structured JSON logs to Loki. Grafana's Loki datasource includes derived fields that link `trace_id` directly to Jaeger — click a trace ID in any log line to jump to the full span hierarchy. Logs dashboard at `localhost:3001` provides log volume by level, error filtering, per-service breakdown, and live tail. Zero application code changes — all integration at infrastructure level.

---

## Development Roadmap

This roadmap is designed to progressively answer the hard questions from "Why This Project Exists" while building production-grade ML infrastructure skills.

---

### Stage 1: Shadow Mode (Challenger Pattern)

**Status:** Complete

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

**Status:** Complete

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

**Status:** Complete

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

### Stage 4: Model Registry Service

**Status:** Complete

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

### Stage 5: Centralized Logging (Grafana Loki)

**Status:** Complete

**What it is:**
Centralized log aggregation using Grafana Loki + Promtail. All container logs are collected, parsed, and queryable in Grafana with trace-log correlation.

```
Docker containers → Promtail (Docker socket discovery) → Loki → Grafana
                                                                    ↓
                                                          Click trace_id → Jaeger
```

**Why it matters:**
- Completes the **three pillars of observability**: metrics (Prometheus), traces (Jaeger), logs (Loki)
- Query logs by level, service, trace_id without SSH-ing into containers
- Trace-log correlation: click a trace_id in any log to jump to the full Jaeger trace
- Zero application code changes — pure infrastructure integration

**What you'll learn:**
- Log aggregation architecture (shipper → store → query)
- Promtail pipeline stages (JSON parsing, label extraction)
- Loki's low-cardinality label model vs high-cardinality detected fields
- Grafana derived fields for cross-datasource linking

**Key components built:**
| Component | Purpose |
|-----------|---------|
| Loki | Log storage with LogQL query language |
| Promtail | Docker service discovery + log shipping |
| Grafana datasource | Loki with derived fields linking trace_id → Jaeger |
| Logs dashboard | Volume by level, errors, per-service breakdown, live tail |

**Success criteria:**
- All container logs queryable in Grafana via Loki
- Can filter by level, container, and trace_id
- Clicking trace_id in logs opens the corresponding Jaeger trace
- Pre-built dashboard loads with all panels populated

---

### Roadmap Summary

| Stage | Focus | Key Question Answered |
|-------|-------|----------------------|
| 1. Shadow Mode | Safe comparison | "Is the new model behaving correctly?" |
| 2. Canary | Safe rollout | "Does the new model work for real users?" |
| 3. Tracing | Debuggability | "Why was this specific request slow/broken?" |
| 4. Registry | Dynamic management | "How do we manage models without redeploying?" |
| 5. Logging | Full observability | "What happened across all services for this request?" |

Each stage builds on the previous. Shadow mode is prerequisite for canary (you should shadow first). Tracing becomes valuable once you have multiple code paths (shadow + canary). Registry is optional but enables more sophisticated patterns. Centralized logging ties everything together — metrics tell you *what*, traces tell you *where*, logs tell you *why*.

---

## Guiding Principle

> Treat ML inference as **backend engineering with math inside**, not magic.

Clarity, correctness, and operability come first.
