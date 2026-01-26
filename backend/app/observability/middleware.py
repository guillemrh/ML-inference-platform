"""HTTP request timing middleware for Prometheus metrics."""

import time
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.observability.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records HTTP request metrics.

    Records:
    - Total request count by method, endpoint, status
    - Request duration histogram by method, endpoint

    Note: Excludes /metrics endpoint to avoid recursive counting.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        endpoint = self._get_endpoint_path(request)
        method = request.method

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - start_time

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)

    def _get_endpoint_path(self, request: Request) -> str:
        """
        Get the route path pattern for the request.

        Uses the route pattern (e.g., /items/{id}) rather than
        the actual path (e.g., /items/123) to avoid high cardinality.
        """
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "path"):
                return route.path

        return request.url.path
