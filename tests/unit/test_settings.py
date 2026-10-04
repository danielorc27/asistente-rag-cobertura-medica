"""Pruebas de la configuración centralizada (Fase 1)."""

from pathlib import Path

import pytest
from app.config.settings import Settings


@pytest.mark.unit
class TestSettings:
    def test_defaults_are_valid(self) -> None:
        settings = Settings(_env_file=None)
        assert settings.openai_model == "gpt-4.1"
        assert settings.embedding_model == "text-embedding-3-small"
        assert settings.top_k_results == 5
        assert settings.chunk_size == 1000
        assert settings.chunk_overlap == 200
        assert settings.documents_path == Path("documents")

    def test_env_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
        monkeypatch.setenv("TOP_K_RESULTS", "7")
        monkeypatch.setenv("MIN_SIMILARITY_SCORE", "0.4")
        settings = Settings(_env_file=None)
        assert settings.openai_model == "gpt-4.1-mini"
        assert settings.top_k_results == 7
        assert settings.min_similarity_score == 0.4

    def test_invalid_values_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TOP_K_RESULTS", "0")
        with pytest.raises(ValueError):
            Settings(_env_file=None)
