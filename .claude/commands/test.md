# /test

Run the test suite inside the Docker container.

## Usage

```
/test           # Run all tests
/test <path>    # Run specific test file or directory
```

## Instructions

1. Ensure Docker containers are running:
   ```bash
   docker-compose ps
   ```
   If not running, start them first:
   ```bash
   docker-compose up -d --build
   ```

2. Run pytest inside the backend container:
   ```bash
   docker-compose exec backend pytest -v
   ```

3. For specific tests:
   ```bash
   docker-compose exec backend pytest -v tests/test_health.py
   ```

4. For coverage report:
   ```bash
   docker-compose exec backend pytest --cov=app --cov-report=term-missing
   ```

## Expected Output

- All tests should pass
- Report any failures with full traceback
- If tests fail, do NOT proceed with PR creation

## Post-Test Actions

- If all tests pass: Proceed with next steps
- If tests fail: Fix the issues before continuing
- Always report test results to the user
