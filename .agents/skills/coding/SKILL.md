---
name: "Python Coding"
description: "Python coding standards, type hints, and testing patterns for this project"
---

# Python Coding Skill

This skill covers Python coding standards and patterns used in the ML Inference Platform.

## Topics

| Document | Description |
|----------|-------------|
| [python.md](python.md) | Python language standards and patterns |
| [testing.md](testing.md) | Testing philosophy and patterns |

## Quick Reference

### Code Style
- Python 3.11+ features encouraged
- Type hints on all function signatures
- Pydantic for data validation
- Structured logging (JSON in production)

### Linting & Formatting
- **ruff** for linting (fast, comprehensive)
- **black** for code formatting (consistent style)
- Run `/lint` before committing

### Testing
- All code requires tests
- Tests must be fast and deterministic
- Mock external dependencies
