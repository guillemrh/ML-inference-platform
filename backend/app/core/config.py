"""
Configuration management for the ML inference platform.

Loads settings from environment variables with validation and defaults.
"""

from pathlib import Path

from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have sensible defaults for local development.
    Override via environment variables in production.
    """

    # Application
    app_name: str = "ml-inference-platform"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Primary Model
    model_path: Path = Path("/app/models/reactor_model_v1.pkl")
    model_version: str = "v1"

    # Deployment Mode
    deployment_mode: Literal["direct", "shadow", "canary"] = "direct"

    # Secondary Model (used as shadow or canary depending on deployment_mode)
    secondary_model_path: Path = Path("/app/models/reactor_model_v2.pkl")
    secondary_model_version: str = "v2"
    shadow_timeout_ms: int = 500  # Max time to wait for shadow model

    # Canary
    canary_weight: int = 0  # Percentage of traffic routed to canary (0-100)

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "protected_namespaces": (),  # Allow model_ prefix in field names
    }


# Global settings instance
settings = Settings()
