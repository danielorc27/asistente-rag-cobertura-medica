"""Pruebas E2E de la API REST (Fase 6, §11.6).

Levantan la aplicación completa con un contenedor de dependencias
simuladas (sin OpenAI real, sin Chroma real) y los documentos reales.
"""

import json
import re
from pathlib import Path

import pytest
from app.application.dto.indexing import IndexingMode
from app.config.dependencies import Container
from app.config.settings import Settings
from app.domain.providers.llm_provider import LLMProvider, LLMRequest, LLMResult
from app.main import create_app
from fastapi.testclient import TestClient

from tests.fixtures.affiliates import make_affiliate
from tests.mocks.in_memory import (
    DeterministicEmbeddingProvider,
    InMemoryAffiliateRepository,
    InMemoryIndexStateRepository,
    InMemoryVectorStore,
    StubLLMProvider,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REINDEX_KEY = "clave-de-prueba"


class CitingStubLLM(LLMProvider):
    """Stub que cita el primer chunk_id presente en el prompt recibido."""

    def generate(self, request: LLMRequest) -> LLMResult:
        match = re.search(r"\[([a-z0-9_]+_\d{5})\]", request.user)
        chunk_id = match.group(1) if match else "desconocido"
        return LLMResult(
            text=json.dumps(
                {
                    "status": "APPROVED",
                    "summary": "La solicitud procede.",
                    "reasoning": "La evidencia respalda la cobertura del procedimiento.",
                    "citations": [chunk_id],
                    "warnings": [],
                }
            ),
            model="stub-model",
            input_tokens=100,
            output_tokens=50,
            latency_ms=5.0,
        )


def _test_container(llm: LLMProvider | None = None, reindex_key: str = REINDEX_KEY) -> Container:
    settings = Settings(
        _env_file=None,
        openai_api_key="test-key",
        documents_path=PROJECT_ROOT / "documents",
        affiliates_file=PROJECT_ROOT / "data" / "BD_afiliados.xlsx",
        min_similarity_score=0.05,
        reindex_api_key=reindex_key,
    )
    container = Container(settings=settings)
    container.__dict__["vector_store"] = InMemoryVectorStore()
    container.__dict__["embedding_provider"] = DeterministicEmbeddingProvider()
    container.__dict__["index_state_repository"] = InMemoryIndexStateRepository()
    container.__dict__["llm_provider"] = llm or CitingStubLLM()
    container.__dict__["affiliate_repository"] = InMemoryAffiliateRepository(
        [make_affiliate(affiliate_id="A-00001")]
    )
    return container


def _client(container: Container, index: bool = True) -> TestClient:
    if index:
        container.indexing_service.run(IndexingMode.FULL)
    return TestClient(create_app(container))


QUESTION = "¿Cuáles son los periodos de carencia para imágenes diagnósticas del plan?"


@pytest.mark.e2e
class TestQueryEndpoint:
    def test_query_happy_path(self) -> None:
        client = _client(_test_container())
        response = client.post("/query", json={"affiliate_id": "A-00001", "question": QUESTION})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "APPROVED"
        assert body["evidence"], "La respuesta debe citar evidencia"
        assert body["evidence_strength"] in ("PARTIAL", "STRONG")
        assert body["trace"]["trace_id"]
        assert body["trace"]["prompt_version"] == "1.0"

    def test_unknown_affiliate_returns_404(self) -> None:
        client = _client(_test_container())
        response = client.post("/query", json={"affiliate_id": "A-99999", "question": QUESTION})
        assert response.status_code == 404
        assert response.json()["error"] == "affiliate_not_found"

    def test_invalid_body_returns_422(self) -> None:
        client = _client(_test_container())
        response = client.post("/query", json={"affiliate_id": "", "question": "x"})
        assert response.status_code == 422

    def test_invalid_llm_response_returns_502(self) -> None:
        client = _client(_test_container(llm=StubLLMProvider(reply="texto sin JSON")))
        response = client.post("/query", json={"affiliate_id": "A-00001", "question": QUESTION})
        assert response.status_code == 502
        assert response.json()["error"] == "llm_response_invalid"


@pytest.mark.e2e
class TestReindexEndpoint:
    def test_reindex_requires_api_key(self) -> None:
        client = _client(_test_container(), index=False)
        assert client.post("/reindex", json={}).status_code == 401
        wrong = client.post("/reindex", json={}, headers={"X-API-Key": "incorrecta"})
        assert wrong.status_code == 401

    def test_reindex_disabled_without_configured_key(self) -> None:
        client = _client(_test_container(reindex_key=""), index=False)
        response = client.post("/reindex", json={}, headers={"X-API-Key": "cualquiera"})
        assert response.status_code == 503

    def test_reindex_with_valid_key_indexes_documents(self) -> None:
        client = _client(_test_container(), index=False)
        response = client.post(
            "/reindex", json={"mode": "FULL"}, headers={"X-API-Key": REINDEX_KEY}
        )
        assert response.status_code == 200
        body = response.json()
        assert len(body["documents_processed"]) == 3
        assert body["chunks_created"] > 0


@pytest.mark.e2e
class TestWebUI:
    def test_root_serves_interface(self) -> None:
        client = _client(_test_container(), index=False)
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Asistente de Validación de Cobertura" in response.text
        assert "/query" in response.text  # la UI consume la misma API


@pytest.mark.e2e
class TestDiagnostics:
    def test_health_reports_component_status(self) -> None:
        client = _client(_test_container())
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["vector_store_available"] is True
        assert body["index_ready"] is True
        assert body["affiliate_repository_available"] is True
        assert body["llm_configured"] is True
        assert body["indexed_chunks"] > 0

    def test_metrics_counts_requests(self) -> None:
        client = _client(_test_container())
        client.get("/health")
        client.post("/query", json={"affiliate_id": "A-99999", "question": QUESTION})
        response = client.get("/metrics")
        assert response.status_code == 200
        body = response.json()
        assert body["requests"].get("/health") == 1
        assert body["errors_by_category"].get("affiliate_not_found") == 1
        assert "uptime_seconds" in body
