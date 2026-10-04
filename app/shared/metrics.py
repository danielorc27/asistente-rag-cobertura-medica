"""Colector de métricas de operación en memoria (§9.14).

Componente reutilizable sin lógica de negocio. Registra contadores por
endpoint, errores por categoría y latencias agregadas.
"""

import threading
import time
from collections import defaultdict


class MetricsCollector:
    """Métricas simples del proceso; thread-safe."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._started_at = time.time()
        self._requests: dict[str, int] = defaultdict(int)
        self._errors: dict[str, int] = defaultdict(int)
        self._latency_total_ms: dict[str, float] = defaultdict(float)

    def record_request(self, endpoint: str, latency_ms: float, error: str | None = None) -> None:
        with self._lock:
            self._requests[endpoint] += 1
            self._latency_total_ms[endpoint] += latency_ms
            if error:
                self._errors[error] += 1

    def record_error(self, category: str) -> None:
        """Registra un error clasificado sin alterar el conteo de requests."""
        with self._lock:
            self._errors[category] += 1

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            average_latency = {
                endpoint: round(self._latency_total_ms[endpoint] / count, 2)
                for endpoint, count in self._requests.items()
                if count
            }
            return {
                "uptime_seconds": round(time.time() - self._started_at, 1),
                "requests": dict(self._requests),
                "errors_by_category": dict(self._errors),
                "average_latency_ms": average_latency,
            }
