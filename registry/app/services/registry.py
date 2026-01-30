"""Business logic for model registry operations."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import ActiveDeployment, MLModel, ModelHistory


def register_model(db: Session, name: str, version: str, file_path: str, metadata: dict | None = None) -> MLModel:
    existing = db.query(MLModel).filter(MLModel.name == name, MLModel.version == version).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Model '{name}' version '{version}' already exists")

    model = MLModel(name=name, version=version, file_path=file_path, status="registered", metadata_=metadata)
    db.add(model)
    db.flush()

    history = ModelHistory(model_id=model.id, action="registered", to_status="registered")
    db.add(history)
    db.commit()
    db.refresh(model)
    return model


def list_models(db: Session, name: str | None = None, status: str | None = None) -> list[MLModel]:
    query = db.query(MLModel)
    if name:
        query = query.filter(MLModel.name == name)
    if status:
        query = query.filter(MLModel.status == status)
    return query.order_by(MLModel.created_at.desc()).all()


def promote_model(
    db: Session, model_id: int, deployment_mode: str, performed_by: str | None = None, reason: str | None = None
) -> MLModel:
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    old_status = model.status
    model.status = "active"

    # Upsert active deployment
    active = (
        db.query(ActiveDeployment)
        .filter(ActiveDeployment.model_name == model.name, ActiveDeployment.deployment_mode == deployment_mode)
        .first()
    )
    if active:
        # Deprecate the previously active model
        prev_model = db.query(MLModel).filter(MLModel.id == active.model_id).first()
        if prev_model and prev_model.id != model.id:
            prev_model.status = "deprecated"
            db.add(
                ModelHistory(
                    model_id=prev_model.id,
                    action="deprecated",
                    from_status="active",
                    to_status="deprecated",
                    performed_by=performed_by,
                    reason=f"Replaced by model {model.id}",
                )
            )
        active.model_id = model.id
    else:
        active = ActiveDeployment(model_name=model.name, deployment_mode=deployment_mode, model_id=model.id)
        db.add(active)

    db.add(
        ModelHistory(
            model_id=model.id,
            action="promoted",
            from_status=old_status,
            to_status="active",
            performed_by=performed_by,
            reason=reason,
        )
    )
    db.commit()
    db.refresh(model)
    return model


def get_active_model(db: Session, name: str, deployment_mode: str) -> dict | None:
    active = (
        db.query(ActiveDeployment)
        .filter(ActiveDeployment.model_name == name, ActiveDeployment.deployment_mode == deployment_mode)
        .first()
    )
    if not active:
        return None

    model = db.query(MLModel).filter(MLModel.id == active.model_id).first()
    if not model:
        return None

    return {
        "model_id": model.id,
        "name": model.name,
        "version": model.version,
        "file_path": model.file_path,
        "deployment_mode": active.deployment_mode,
        "activated_at": active.activated_at,
    }


def rollback_model(
    db: Session, name: str, deployment_mode: str, performed_by: str | None = None, reason: str | None = None
) -> MLModel:
    active = (
        db.query(ActiveDeployment)
        .filter(ActiveDeployment.model_name == name, ActiveDeployment.deployment_mode == deployment_mode)
        .first()
    )
    if not active:
        raise HTTPException(status_code=404, detail=f"No active deployment for '{name}' in mode '{deployment_mode}'")

    current_model = db.query(MLModel).filter(MLModel.id == active.model_id).first()

    # Find the previous active version from history
    prev_promotion = (
        db.query(ModelHistory)
        .join(MLModel)
        .filter(MLModel.name == name, ModelHistory.action == "promoted", ModelHistory.model_id != current_model.id)
        .order_by(ModelHistory.created_at.desc())
        .first()
    )
    if not prev_promotion:
        raise HTTPException(status_code=404, detail="No previous version to rollback to")

    prev_model = db.query(MLModel).filter(MLModel.id == prev_promotion.model_id).first()

    # Deprecate current, activate previous
    current_model.status = "deprecated"
    prev_model.status = "active"
    active.model_id = prev_model.id

    db.add(
        ModelHistory(
            model_id=current_model.id,
            action="rollback",
            from_status="active",
            to_status="deprecated",
            performed_by=performed_by,
            reason=reason,
        )
    )
    db.add(
        ModelHistory(
            model_id=prev_model.id,
            action="rollback",
            from_status="deprecated",
            to_status="active",
            performed_by=performed_by,
            reason=reason,
        )
    )
    db.commit()
    db.refresh(prev_model)
    return prev_model


def get_model_history(db: Session, model_id: int) -> list[ModelHistory]:
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return db.query(ModelHistory).filter(ModelHistory.model_id == model_id).order_by(ModelHistory.created_at.desc()).all()
