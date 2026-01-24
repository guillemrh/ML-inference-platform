# /add-endpoint

Scaffold a new API endpoint with proper structure.

## Usage

```
/add-endpoint <name>           # Create endpoint with given name
/add-endpoint inference        # Example: creates inference endpoint
```

## Instructions

When creating a new endpoint, generate the following files:

### 1. Route File
Location: `backend/app/api/routes/<name>.py`

```python
"""
<Name> API endpoint.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.<name> import <Name>Request, <Name>Response
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/<name>", response_model=<Name>Response)
async def <name>_endpoint(request: <Name>Request) -> <Name>Response:
    """
    <Description of what this endpoint does>.
    """
    logger.info(
        "<Name> request received",
        extra={"extra_fields": {"request_id": "TODO"}}
    )

    # TODO: Implement logic

    return <Name>Response(
        # TODO: Return fields
    )
```

### 2. Schema File
Location: `backend/app/schemas/<name>.py`

```python
"""
<Name> request/response schemas.
"""

from pydantic import BaseModel, Field


class <Name>Request(BaseModel):
    """Request schema for <name> endpoint."""
    # TODO: Add request fields
    pass


class <Name>Response(BaseModel):
    """Response schema for <name> endpoint."""
    # TODO: Add response fields
    pass
```

### 3. Test File
Location: `backend/tests/test_<name>.py`

```python
"""
Tests for <name> endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class Test<Name>Endpoint:
    """Tests for /<name> endpoint."""

    def test_<name>_success(self):
        """Test successful <name> request."""
        response = client.post(
            "/<name>",
            json={
                # TODO: Add test request
            }
        )
        assert response.status_code == 200
        # TODO: Add assertions

    def test_<name>_invalid_input(self):
        """Test <name> with invalid input."""
        response = client.post(
            "/<name>",
            json={}
        )
        assert response.status_code == 422  # Validation error
```

### 4. Register Route
Update `backend/app/main.py`:

```python
from app.api.routes import health, <name>

# In create_app():
app.include_router(<name>.router, tags=["<name>"])
```

### 5. Update __init__.py files
- `backend/app/api/routes/__init__.py`
- `backend/app/schemas/__init__.py`

## Post-Creation Checklist

- [ ] Route file created
- [ ] Schema file created
- [ ] Test file created
- [ ] Route registered in main.py
- [ ] __init__.py files updated
- [ ] Tests pass with `/test`
