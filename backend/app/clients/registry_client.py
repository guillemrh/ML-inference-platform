"""HTTP client for querying the Model Registry service."""

from dataclasses import dataclass
from pathlib import Path

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RegistryModelInfo:
    """Model info returned from the registry."""

    model_id: int
    name: str
    version: str
    file_path: Path
    deployment_mode: str


class RegistryClient:
    """Client for the Model Registry API."""

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def get_active_model(
        self, name: str, mode: str = "primary"
    ) -> RegistryModelInfo | None:
        """Query the registry for the active model in a given deployment mode."""
        try:
            response = httpx.get(
                f"{self._base_url}/api/v1/models/active",
                params={"name": name, "mode": mode},
                timeout=self._timeout,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return RegistryModelInfo(
                model_id=data["model_id"],
                name=data["name"],
                version=data["version"],
                file_path=Path(data["file_path"]),
                deployment_mode=data["deployment_mode"],
            )
        except httpx.HTTPError as e:
            logger.error(
                "Failed to query registry",
                extra={"extra_fields": {"error": str(e), "name": name, "mode": mode}},
            )
            return None

    def health_check(self) -> bool:
        """Check if the registry service is reachable."""
        try:
            response = httpx.get(f"{self._base_url}/health", timeout=self._timeout)
            return response.status_code == 200
        except httpx.HTTPError:
            return False
