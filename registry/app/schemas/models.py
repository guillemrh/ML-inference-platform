"""Pydantic schemas for model registry API."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ModelRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=100)
    file_path: str = Field(..., min_length=1, max_length=500)
    metadata: dict[str, Any] | None = None


class ModelResponse(BaseModel):
    id: int
    name: str
    version: str
    file_path: str
    status: str
    metadata: dict[str, Any] | None = Field(None, validation_alias="metadata_")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class ModelPromoteRequest(BaseModel):
    deployment_mode: str = Field(default="primary", pattern="^(primary|shadow|canary)$")
    performed_by: str | None = None
    reason: str | None = None


class ModelRollbackRequest(BaseModel):
    name: str
    deployment_mode: str = Field(default="primary", pattern="^(primary|shadow|canary)$")
    performed_by: str | None = None
    reason: str | None = None


class ActiveModelResponse(BaseModel):
    model_id: int
    name: str
    version: str
    file_path: str
    deployment_mode: str
    activated_at: datetime


class HistoryResponse(BaseModel):
    id: int
    action: str
    from_status: str | None
    to_status: str
    performed_by: str | None
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
