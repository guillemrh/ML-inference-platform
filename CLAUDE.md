# ML Inference Platform - Claude Context

## Project Overview

This is a **production-oriented ML inference system** focused on correctness, latency, observability, and operational clarity. The project is about **serving ML models as real software systems**, not training them.

## Tech Stack

- **Language:** Python 3.11+
- **API Framework:** FastAPI
- **ML Runtime:** Lightweight Python model wrappers (scikit-learn, PyTorch)
- **Metrics:** Prometheus-compatible
- **Containers:** Docker + docker-compose
- **Testing:** pytest

## Development Workflow

### Branch Strategy
- **Feature branches** for all changes
- **PR-based workflow**: feature branch → PR → review → merge to master
- Never commit directly to master

### Docker-First Development
- All code runs in Docker containers
- Never install dependencies directly on host machine
- Use `docker-compose` for local development
- Tests run inside containers

### Testing Requirements (Strict)
- **All code changes require tests**
- Refuse to merge/PR without accompanying tests
- Run tests automatically after code changes
- Tests must pass before PR creation

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── api/routes/          # API endpoints
│   ├── core/                # Config, logging
│   ├── models/              # ML model loaders
│   ├── schemas/             # Pydantic models
│   ├── services/            # Business logic
│   └── observability/       # Metrics, health
├── tests/                   # pytest tests
├── Dockerfile
└── requirements.txt
```

## Key Files

| File | Purpose |
|------|---------|
| [main.py](backend/app/main.py) | Application factory, lifespan management |
| [health.py](backend/app/api/routes/health.py) | Health check endpoint |
| [config.py](backend/app/core/config.py) | Environment-based settings |
| [logging.py](backend/app/core/logging.py) | Structured JSON logging |
| [docker-compose.yml](docker-compose.yml) | Container orchestration |

## Commands

| Command | Purpose |
|---------|---------|
| `/test` | Run pytest in Docker container |
| `/lint` | Run ruff linter and formatter |
| `/add-endpoint` | Scaffold a new API endpoint |

## Subagents

| Agent | Model | Triggers On |
|-------|-------|-------------|
| `model-reviewer` | opus | Changes to `models/`, `services/inference*` |
| `api-reviewer` | sonnet | Changes to `api/routes/`, `schemas/` |

## Code Standards

See [.agents/skills/](.agents/skills/) for detailed standards:
- [coding/python.md](.agents/skills/coding/python.md) - Python standards, type hints, Pydantic
- [coding/testing.md](.agents/skills/coding/testing.md) - Testing patterns and requirements
- [inference/schemas.md](.agents/skills/inference/schemas.md) - API request/response design

## Non-Goals

Do NOT implement:
- Model training pipelines
- AutoML or hyperparameter tuning
- UI dashboards
- Distributed training
- GPU support (for now)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | ml-inference-platform | Application name |
| `ENVIRONMENT` | development | Environment (development/production) |
| `LOG_LEVEL` | INFO | Logging level |
| `API_HOST` | 0.0.0.0 | API bind host |
| `API_PORT` | 8000 | API bind port |
