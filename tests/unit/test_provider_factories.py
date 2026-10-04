"""Pruebas de los factories de proveedores (Fase 3, §3.15)."""

import pytest
from app.config.settings import Settings
from app.domain.exceptions.errors import ConfigurationError
from app.infrastructure.chunking.recursive_chunk_strategy import RecursiveChunkStrategy
from app.infrastructure.factories.provider_factories import (
    create_chunk_strategy,
    create_document_loaders,
    create_embedding_provider,
    create_llm_provider,
    create_vector_store,
)


def _settings(**overrides: object) -> Settings:
    return Settings(_env_file=None, **overrides)  # type: ignore[arg-type]


@pytest.mark.unit
class TestProviderFactories:
    def test_unknown_llm_provider_raises(self) -> None:
        with pytest.raises(ConfigurationError, match="LLM_PROVIDER"):
            create_llm_provider(_settings(llm_provider="acme"))

    def test_unknown_embedding_provider_raises(self) -> None:
        with pytest.raises(ConfigurationError, match="EMBEDDING_PROVIDER"):
            create_embedding_provider(_settings(embedding_provider="acme"))

    def test_unknown_vector_store_raises(self) -> None:
        with pytest.raises(ConfigurationError, match="VECTOR_STORE_PROVIDER"):
            create_vector_store(_settings(vector_store_provider="acme"))

    def test_default_chunk_strategy_uses_settings(self) -> None:
        strategy = create_chunk_strategy(_settings(chunk_size=500, chunk_overlap=50))
        assert isinstance(strategy, RecursiveChunkStrategy)

    def test_document_loaders_include_word(self) -> None:
        loaders = create_document_loaders(_settings())
        assert len(loaders) == 1
