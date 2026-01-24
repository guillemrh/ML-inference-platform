# /lint

Run linting and formatting checks using ruff inside Docker.

## Usage

```
/lint           # Check for issues
/lint --fix     # Auto-fix issues
```

## Instructions

1. Ensure Docker containers are running:
   ```bash
   docker-compose ps
   ```

2. Run ruff linter (check mode):
   ```bash
   docker-compose exec backend ruff check app/ tests/
   ```

3. Run ruff formatter (check mode):
   ```bash
   docker-compose exec backend ruff format --check app/ tests/
   ```

4. To auto-fix issues:
   ```bash
   docker-compose exec backend ruff check --fix app/ tests/
   docker-compose exec backend ruff format app/ tests/
   ```

## Linting Rules

This project uses ruff with the following focus:
- **E**: pycodestyle errors
- **F**: Pyflakes
- **I**: isort (import sorting)
- **UP**: pyupgrade (modern Python syntax)
- **B**: flake8-bugbear (common bugs)

## Expected Output

- Report all linting errors found
- Suggest fixes for common issues
- If using `--fix`, report what was auto-fixed

## Notes

- Linting should pass before creating PRs
- Format code before committing
- If ruff is not installed in container, add it to requirements.txt first
