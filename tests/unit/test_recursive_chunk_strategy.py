"""Pruebas de la estrategia de chunking (Fase 3, §11.8)."""

import pytest
from app.infrastructure.chunking.recursive_chunk_strategy import RecursiveChunkStrategy


@pytest.mark.unit
class TestRecursiveChunkStrategy:
    def test_short_text_single_chunk(self) -> None:
        strategy = RecursiveChunkStrategy(chunk_size=1000, chunk_overlap=200)
        assert strategy.split("Texto corto.") == ["Texto corto."]

    def test_empty_text_returns_no_chunks(self) -> None:
        strategy = RecursiveChunkStrategy(chunk_size=1000, chunk_overlap=200)
        assert strategy.split("") == []
        assert strategy.split("   \n ") == []

    def test_chunks_respect_configured_size(self) -> None:
        strategy = RecursiveChunkStrategy(chunk_size=100, chunk_overlap=20)
        text = "\n\n".join(f"Párrafo número {i} con contenido de prueba." for i in range(30))
        chunks = strategy.split(text)
        assert len(chunks) > 1
        assert all(len(c) <= 100 for c in chunks)

    def test_no_content_lost(self) -> None:
        strategy = RecursiveChunkStrategy(chunk_size=80, chunk_overlap=10)
        sentences = [f"La regla {i} aplica al plan Premium." for i in range(20)]
        chunks = strategy.split("\n\n".join(sentences))
        joined = " ".join(chunks)
        for sentence in sentences:
            assert sentence in joined

    def test_words_never_split(self) -> None:
        strategy = RecursiveChunkStrategy(chunk_size=50, chunk_overlap=10)
        words = [f"palabra{i:03d}" for i in range(40)]
        chunks = strategy.split(" ".join(words))
        reconstructed = set()
        for chunk in chunks:
            reconstructed.update(chunk.split())
        assert reconstructed == set(words)

    def test_overlap_present_between_consecutive_chunks(self) -> None:
        strategy = RecursiveChunkStrategy(chunk_size=100, chunk_overlap=30)
        text = " ".join(f"token{i:03d}" for i in range(60))
        chunks = strategy.split(text)
        assert len(chunks) > 1
        for first, second in zip(chunks, chunks[1:], strict=False):
            tail_words = set(first.split()[-3:])
            assert tail_words & set(second.split()), "No hay overlap entre chunks"

    def test_overlap_must_be_smaller_than_size(self) -> None:
        with pytest.raises(ValueError):
            RecursiveChunkStrategy(chunk_size=100, chunk_overlap=100)
