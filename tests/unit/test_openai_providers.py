"""Pruebas de los adapters OpenAI con clientes simulados (Fase 3, §11.13)."""

import pytest
from app.domain.exceptions.errors import LLMProviderError
from app.domain.providers.llm_provider import LLMRequest
from app.infrastructure.embeddings.openai_embedding_provider import OpenAIEmbeddingProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider

from tests.mocks.openai_fakes import FakeEmbeddingClient, FakeOpenAIClient


@pytest.mark.unit
class TestOpenAIProvider:
    def test_generate_returns_result_with_metadata(self) -> None:
        provider = OpenAIProvider(api_key="k", model="gpt-4.1", client=FakeOpenAIClient())
        result = provider.generate(LLMRequest(system="sys", user="pregunta"))
        assert result.text == '{"ok": true}'
        assert result.model == "gpt-4.1-fake"
        assert result.input_tokens == 100
        assert result.output_tokens == 50
        assert result.latency_ms is not None and result.latency_ms >= 0

    def test_json_output_requests_json_format(self) -> None:
        client = FakeOpenAIClient()
        provider = OpenAIProvider(api_key="k", model="gpt-4.1", client=client)
        provider.generate(LLMRequest(system="s", user="u", json_output=True))
        assert client.chat.completions.last_kwargs["response_format"] == {"type": "json_object"}

    def test_empty_response_raises_controlled_error(self) -> None:
        provider = OpenAIProvider(api_key="k", model="gpt-4.1", client=FakeOpenAIClient(reply=""))
        with pytest.raises(LLMProviderError):
            provider.generate(LLMRequest(system="s", user="u"))

    def test_sdk_failure_wrapped_as_domain_error(self) -> None:
        class BrokenClient:
            class chat:  # noqa: N801
                class completions:  # noqa: N801
                    @staticmethod
                    def create(**kwargs: object) -> None:
                        raise TimeoutError("timeout")

        provider = OpenAIProvider(api_key="k", model="gpt-4.1", client=BrokenClient())
        with pytest.raises(LLMProviderError):
            provider.generate(LLMRequest(system="s", user="u"))


@pytest.mark.unit
class TestOpenAIEmbeddingProvider:
    def test_embeddings_preserve_input_order(self) -> None:
        provider = OpenAIEmbeddingProvider(
            api_key="k", model="emb", client=FakeEmbeddingClient(dimensions=3)
        )
        result = provider.embed_texts(["a", "b", "c"])
        # el fake devuelve los items desordenados; el provider debe reordenar
        assert result == [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], [2.0, 2.0, 2.0]]

    def test_batching_splits_large_inputs(self) -> None:
        client = FakeEmbeddingClient()
        provider = OpenAIEmbeddingProvider(api_key="k", model="emb", client=client)
        provider.embed_texts([f"t{i}" for i in range(150)])
        assert [len(c) for c in client.embeddings.calls] == [100, 50]

    def test_embed_query_returns_single_vector(self) -> None:
        provider = OpenAIEmbeddingProvider(
            api_key="k", model="emb", client=FakeEmbeddingClient(dimensions=2)
        )
        assert provider.embed_query("consulta") == [0.0, 0.0]

    def test_null_index_preserves_response_order(self) -> None:
        """Endpoints compatibles (Gemini) devuelven index=None (§8.17)."""
        provider = OpenAIEmbeddingProvider(
            api_key="k", model="emb", client=FakeEmbeddingClient(dimensions=2, null_index=True)
        )
        # El fake invierte el orden de los items; con index=None debe
        # preservarse el orden de la respuesta tal cual llega.
        assert provider.embed_texts(["a", "b"]) == [[1.0, 1.0], [0.0, 0.0]]
