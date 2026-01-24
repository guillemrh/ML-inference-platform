---
name: "Workflows"
description: "Development workflows including Docker usage, git branching, and PR process"
---

# Workflows Skill

This skill covers development workflows for the ML Inference Platform.

## Topics

| Document | Description |
|----------|-------------|
| [docker.md](docker.md) | Docker-first development workflow |
| [pr-workflow.md](pr-workflow.md) | Feature branch and PR process |

## Core Principles

1. **Docker-first** - All code runs in containers, never on host
2. **Feature branches** - All changes go through branches and PRs
3. **Tests required** - No PR without passing tests
4. **Ask permission** - Before destructive actions

## Quick Reference

### Starting Work
```bash
# Create feature branch
git checkout -b feature/my-feature

# Start containers
docker-compose up -d --build
```

### During Work
```bash
# Run tests
docker-compose exec backend pytest -v

# Check logs
docker-compose logs -f backend
```

### Finishing Work
```bash
# Ensure tests pass
docker-compose exec backend pytest -v

# Create PR
gh pr create --title "Feature: Description" --body "..."
```
