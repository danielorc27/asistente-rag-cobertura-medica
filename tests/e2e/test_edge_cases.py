"""Casos límite del sistema completo (Fase 7, §11.15)."""

import pytest
from app.domain.exceptions.errors import LLMProviderError
from app.domain.providers.llm_provider import LLMProvider, LLMRequest, LLMResult
from app.main import create_app
from fastapi.testclient import TestClient

from tests.e2e.test_api import QUESTION, _client, _test_container


class FailingLLM(LLMProvider):
    """Simula proveedor LLM caído (§11.15: sin conexión al proveedor)."""

    def generate(self, request: LLMRequest) -> LLMResult:
        raise LLMProviderError("Timeout de conexión con el proveedor.")


@pytest.mark.e2e
class TestEdgeCases:
    def test_empty_index_returns_insufficient_information(self) -> None:
        """Vector store vacío (§11.15): responde sin inventar, sin llamar al LLM."""
        client = _client(_test_container(llm=FailingLLM()), index=False)
        response = client.post("/query", json={"affiliate_id": "A-00001", "question": QUESTION})
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "INSUFFICIENT_INFORMATION"
        assert body["evidence"] == []
        # FailingLLM habría lanzado 502 si se hubiera invocado: no se invocó.

    def test_llm_provider_down_returns_502(self) -> None:
        client = _client(_test_container(llm=FailingLLM()))
        response = client.post("/query", json={"affiliate_id": "A-00001", "question": QUESTION})
        assert response.status_code == 502
        assert response.json()["error"] == "llm_provider_error"

    def test_very_long_question_is_handled(self) -> None:
        """Consulta muy larga (§11.15): no debe romper el pipeline."""
        client = _client(_test_container())
        long_question = "¿Está cubierta la resonancia? " * 300
        response = client.post(
            "/query", json={"affiliate_id": "A-00001", "question": long_question}
        )
        assert response.status_code in (200, 502)  # nunca 500 sin clasificar

    def test_ambiguous_question_without_procedure(self) -> None:
        """Consulta sin procedimiento identificable (§11.15)."""
        client = _client(_test_container())
        response = client.post(
            "/query", json={"affiliate_id": "A-00001", "question": "hola buenas tardes"}
        )
        assert response.status_code == 200
        # Sin solapamiento léxico → sin evidencia → respuesta honesta.
        assert response.json()["status"] in ("INSUFFICIENT_INFORMATION", "APPROVED")

    def test_health_degraded_without_llm_key(self) -> None:
        container = _test_container()
        container.settings = container.settings.model_copy(update={"openai_api_key": ""})
        client = TestClient(create_app(container))
        body = client.get("/health").json()
        assert body["llm_configured"] is False
        assert body["status"] == "degraded"
