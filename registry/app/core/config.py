"""
Configuration for the Model Registry service.
"""

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Settings loaded from environment variables."""

    # Application
    app_name: str = "ml-model-registry"
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8001

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Database
    database_url: str = "postgresql://registry:registry_password@postgres:5432/model_registry"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }


settings = Settings()
