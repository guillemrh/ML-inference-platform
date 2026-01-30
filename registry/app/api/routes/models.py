"""Model registry API routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.models import (
    ActiveModelResponse,
    HistoryResponse,
    ModelPromoteRequest,
    ModelRegisterRequest,
    ModelResponse,
    ModelRollbackRequest,
)
from app.services.registry import (
    get_active_model,
    get_model_history,
    list_models,
    promote_model,
    register_model,
    rollback_model,
)

router = APIRouter()


@router.post("/models", response_model=ModelResponse, status_code=201)
def register(request: ModelRegisterRequest, db: Session = Depends(get_db)):
    model = register_model(db, request.name, request.version, request.file_path, request.metadata)
    return model


@router.get("/models", response_model=list[ModelResponse])
def list_all(
    name: str | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return list_models(db, name=name, status=status)


@router.get("/models/active", response_model=ActiveModelResponse)
def get_active(
    name: str = Query(...),
    mode: str = Query(default="primary"),
    db: Session = Depends(get_db),
):
    result = get_active_model(db, name, mode)
    if not result:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail=f"No active model for '{name}' in mode '{mode}'")
    return result


@router.post("/models/{model_id}/promote", response_model=ModelResponse)
def promote(model_id: int, request: ModelPromoteRequest, db: Session = Depends(get_db)):
    return promote_model(db, model_id, request.deployment_mode, request.performed_by, request.reason)


@router.post("/models/rollback", response_model=ModelResponse)
def rollback(request: ModelRollbackRequest, db: Session = Depends(get_db)):
    return rollback_model(db, request.name, request.deployment_mode, request.performed_by, request.reason)


@router.get("/models/{model_id}/history", response_model=list[HistoryResponse])
def history(model_id: int, db: Session = Depends(get_db)):
    return get_model_history(db, model_id)
