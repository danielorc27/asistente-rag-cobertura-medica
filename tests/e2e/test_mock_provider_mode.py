"""Modo demo offline: sistema COMPLETO con LLM_PROVIDER=mock (§2.13).

A diferencia del resto de pruebas E2E, aquí no se inyecta ningún doble:
el contenedor usa los factories reales (Chroma real en directorio
temporal, providers mock de Infrastructure). Es la demostración de la
Regla de Oro: cambiar de proveedor es solo configuración.
"""

from pathlib import Path

import pytest
from app.application.reasoning.response_validator import ResponseValidator
from app.config.dependencies import Container
from app.config.settings import Settings
from app.domain.providers.llm_provider import LLMRequest
from app.infrastructure.embeddings.mock_embedding_provider import MockEmbeddingProvider
from app.infrastructure.llm.mock_llm_provider import MockLLMProvider
from app.main import create_app
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.e2e
class TestMockProviderMode:
    def test_full_system_runs_offline_with_mock_providers(self, tmp_path: Path) -> None:
        settings = Settings(
            _env_file=None,
            llm_provider="mock",
            embedding_provider="mock",
            openai_api_key="",  # sin API Key: el punto de la prueba
            documents_path=PROJECT_ROOT / "documents",
            affiliates_file=PROJECT_ROOT / "data" / "BD_afiliados.xlsx",
            vector_db_path=tmp_path / "chroma",
            min_similarity_score=0.05,
            reindex_api_key="demo-key",
        )
        container = Container(settings=settings)  # cableado 100% real
        client = TestClient(create_app(container))

        # Indexación real (Chroma + embeddings mock) vía API protegida.
        reindex = client.post("/reindex", json={"mode": "FULL"}, headers={"X-API-Key": "demo-key"})
        assert reindex.status_code == 200
        assert len(reindex.json()["documents_processed"]) == 3

        # Health: operativo sin API Key gracias al proveedor mock.
        health = client.get("/health").json()
        assert health["llm_configured"] is True
        assert health["index_ready"] is True

        # Consulta completa por el pipeline real.
        response = client.post(
            "/query",
            json={
                "affiliate_id": "A-00001",
                "question": "¿Cuáles son los periodos de carencia para imágenes diagnósticas?",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["trace"]["model"] == "mock-llm"
        assert "SIMULADA" in body["summary"]
        assert body["status"] == "INSUFFICIENT_INFORMATION"  # el mock nunca decide
        assert any("MockLLMProvider" in w for w in body["warnings"])


@pytest.mark.unit
class TestMockProviders:
    def test_mock_llm_output_passes_response_validator(self) -> None:
        prompt = (
            "## Evidencia documental\n\n"
            "[doc1_00001] (fuente: DOC1.docx)\ncontenido uno\n\n---\n\n"
            "[doc2_00005] (fuente: DOC2.docx)\ncontenido dos"
        )
        result = MockLLMProvider().generate(LLMRequest(system="s", user=prompt))
        parsed = ResponseValidator().validate(result.text, {"doc1_00001", "doc2_00005"})
        assert set(parsed.citations) == {"doc1_00001", "doc2_00005"}

    def test_mock_embeddings_deterministic_and_normalized(self) -> None:
        provider = MockEmbeddingProvider()
        first = provider.embed_query("carencia de imágenes diagnósticas")
        second = provider.embed_query("carencia de imágenes diagnósticas")
        assert first == second
        assert abs(sum(v * v for v in first) - 1.0) < 1e-9
