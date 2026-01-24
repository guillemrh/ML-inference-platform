# Docker Workflow

## Philosophy

**Never install dependencies on the host machine.**

All development, testing, and running happens inside Docker containers. This ensures:
- Consistent environments across machines
- No "works on my machine" problems
- Easy cleanup (just delete containers)

## Essential Commands

### Start Development Environment

```bash
# Build and start all services
docker-compose up -d --build

# View running containers
docker-compose ps
```

### Run Commands in Container

```bash
# Run pytest
docker-compose exec backend pytest -v

# Run specific test
docker-compose exec backend pytest -v tests/test_health.py

# Open shell in container
docker-compose exec backend bash

# Run Python script
docker-compose exec backend python -m app.scripts.something
```

### View Logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Stop Environment

```bash
# Stop containers (keep volumes)
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove everything including images
docker-compose down -v --rmi all
```

### Rebuild After Changes

```bash
# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build backend
```

## docker-compose.yml Reference

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ml-inference-backend
    ports:
      - "8003:8000"
    environment:
      - APP_NAME=ml-inference-platform
      - ENVIRONMENT=development
      - LOG_LEVEL=INFO
    volumes:
      # Mount code for hot reload
      - ./backend/app:/app/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

networks:
  default:
    name: ml-inference-network
```

## Volume Mounts

For development, code is mounted into the container:

```yaml
volumes:
  - ./backend/app:/app/app
```

This means:
- Code changes are immediately reflected
- No rebuild needed for Python changes
- Uvicorn hot reload works automatically

## Adding Dependencies

When you need new Python packages:

1. Add to `requirements.txt`:
   ```
   scikit-learn==1.3.0
   ```

2. Rebuild the container:
   ```bash
   docker-compose build backend
   docker-compose up -d backend
   ```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs backend

# Check if port is in use
lsof -i :8003
```

### Tests fail with import errors

```bash
# Rebuild to get new dependencies
docker-compose build --no-cache backend
```

### Changes not reflecting

```bash
# Restart with fresh build
docker-compose down
docker-compose up -d --build
```

### Out of disk space

```bash
# Clean up unused Docker resources
docker system prune -a
```

## Best Practices

1. **Always use docker-compose exec** - Don't install Python locally
2. **Rebuild after requirements.txt changes** - Dependencies aren't auto-installed
3. **Use --build for important changes** - Ensures fresh container
4. **Check logs first** - Most issues are visible in logs
5. **Don't modify container directly** - Changes are lost on restart
