"""
SQLAlchemy ORM models for the model registry.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class MLModel(Base):
    """Model metadata."""

    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    version = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="registered")
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    history = relationship("ModelHistory", back_populates="model", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("name", "version", name="uq_model_name_version"),)


class ModelHistory(Base):
    """Audit log of model state changes."""

    __tablename__ = "model_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    performed_by = Column(String(255), nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    model = relationship("MLModel", back_populates="history")


class ActiveDeployment(Base):
    """Tracks which model is active per deployment mode."""

    __tablename__ = "active_deployments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(255), nullable=False)
    deployment_mode = Column(String(50), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    activated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    model = relationship("MLModel")

    __table_args__ = (
        UniqueConstraint("model_name", "deployment_mode", name="uq_active_deployment"),
    )
