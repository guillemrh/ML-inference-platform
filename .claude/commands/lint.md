# /lint

Run linting and formatting checks inside Docker.

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

3. Run black formatter (check mode):
   ```bash
   docker-compose exec backend black --check app/ tests/
   ```

4. To auto-fix issues:
   ```bash
   docker-compose exec backend ruff check --fix app/ tests/
   docker-compose exec backend black app/ tests/
   ```

## Tools

### Ruff (Linting)
Fast Python linter with these rule sets:
- **E**: pycodestyle errors
- **F**: Pyflakes
- **I**: isort (import sorting)
- **UP**: pyupgrade (modern Python syntax)
- **B**: flake8-bugbear (common bugs)

### Black (Formatting)
Opinionated code formatter:
- Consistent code style
- Line length: 88 characters (default)
- No configuration needed

## Expected Output

- Report all linting errors found
- Suggest fixes for common issues
- If using `--fix`, report what was auto-fixed

## Notes

- Linting and formatting should pass before creating PRs
- Format code before committing
- Required in `requirements.txt`: `ruff`, `black`
