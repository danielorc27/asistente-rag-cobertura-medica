"""Pruebas del colector de métricas (Fase 7, §9.14)."""

import pytest
from app.shared.metrics import MetricsCollector


@pytest.mark.unit
class TestMetricsCollector:
    def test_records_requests_and_latency(self) -> None:
        collector = MetricsCollector()
        collector.record_request("/query", 100.0)
        collector.record_request("/query", 200.0)
        snapshot = collector.snapshot()
        assert snapshot["requests"] == {"/query": 2}
        assert snapshot["average_latency_ms"] == {"/query": 150.0}

    def test_records_errors_by_category(self) -> None:
        collector = MetricsCollector()
        collector.record_request("/query", 10.0, error="http_404")
        collector.record_error("llm_provider_error")
        snapshot = collector.snapshot()
        assert snapshot["errors_by_category"] == {"http_404": 1, "llm_provider_error": 1}

    def test_uptime_present(self) -> None:
        snapshot = MetricsCollector().snapshot()
        assert isinstance(snapshot["uptime_seconds"], float)
