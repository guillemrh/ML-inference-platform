"""Health check endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    status = "healthy" if db_status == "connected" else "degraded"
    return {"status": status, "database": db_status}
