"""Middleware de métricas por request (§9.14)."""

import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response


def register_metrics_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def collect_metrics(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        latency_ms = (time.perf_counter() - started) * 1000
        error = f"http_{response.status_code}" if response.status_code >= 400 else None
        app.state.metrics.record_request(request.url.path, latency_ms, error=error)
        return response
