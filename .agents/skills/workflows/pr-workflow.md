# PR Workflow

## Branch Strategy

```
master (main branch)
  │
  ├── feature/add-inference-endpoint
  ├── feature/model-versioning
  ├── fix/health-check-timeout
  └── refactor/logging-structure
```

## Workflow Steps

### 1. Create Feature Branch

```bash
# Always start from master
git checkout master
git pull origin master

# Create branch with descriptive name
git checkout -b feature/add-inference-endpoint
```

### Branch Naming

| Prefix | Use For |
|--------|---------|
| `feature/` | New functionality |
| `fix/` | Bug fixes |
| `refactor/` | Code restructuring |
| `docs/` | Documentation only |

### 2. Develop and Test

```bash
# Start containers
docker-compose up -d --build

# Make changes...

# Run tests frequently
docker-compose exec backend pytest -v

# Run linter
docker-compose exec backend ruff check app/ tests/
```

### 3. Commit Changes

```bash
# Stage specific files
git add backend/app/api/routes/inference.py
git add backend/tests/test_inference.py

# Commit with clear message
git commit -m "Add inference endpoint with basic prediction support

- Implement POST /predict endpoint
- Add request/response schemas
- Add unit tests for success and error cases"
```

### Commit Message Format

```
<type>: <short description>

<optional longer description>

<optional bullet points of changes>
```

Examples:
- `feat: Add inference endpoint`
- `fix: Handle empty feature list in prediction`
- `refactor: Extract model loading to separate module`
- `test: Add integration tests for health endpoint`

### 4. Push and Create PR

```bash
# Push branch
git push -u origin feature/add-inference-endpoint

# Create PR using GitHub CLI
gh pr create \
  --title "Add inference endpoint" \
  --body "## Summary
- Implements POST /predict endpoint
- Adds request validation
- Returns prediction with model version and latency

## Test Plan
- [x] Unit tests pass
- [x] Manual test with curl
- [ ] Integration test with Docker

## Notes
Uses scikit-learn LogisticRegression for initial implementation."
```

### 5. PR Requirements

Before creating PR:
- [ ] All tests pass (`/test`)
- [ ] Linter passes (`/lint`)
- [ ] New code has tests
- [ ] Commit messages are clear
- [ ] Branch is up to date with master

### 6. After Review

```bash
# If changes requested, make them and push
git add .
git commit -m "Address review feedback: add input validation"
git push

# After approval, merge via GitHub UI or:
gh pr merge --squash
```

### 7. Cleanup

```bash
# Switch back to master
git checkout master
git pull origin master

# Delete local branch
git branch -d feature/add-inference-endpoint
```

## PR Template

```markdown
## Summary
<1-3 bullet points describing what this PR does>

## Changes
- <specific file/component changed>
- <specific file/component changed>

## Test Plan
- [ ] Unit tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Notes
<Any additional context, trade-offs, or future work>
```

## Rules

1. **Never commit directly to master**
2. **Never merge without passing tests**
3. **Never merge without at least one approval** (when working with team)
4. **Always delete branch after merge**
5. **Keep PRs focused** - One feature/fix per PR
