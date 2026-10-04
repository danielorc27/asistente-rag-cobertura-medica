"""Pruebas de integración de ChromaVectorStore con persistencia temporal."""

from pathlib import Path

import pytest
from app.domain.providers.vector_store import VectorRecord
from app.domain.value_objects.document_chunk import DocumentChunk
from app.infrastructure.vectorstore.chroma_vector_store import ChromaVectorStore


def _record(chunk_id: str, doc_id: str, content: str, embedding: list[float]) -> VectorRecord:
    return VectorRecord(
        chunk=DocumentChunk(
            chunk_id=chunk_id,
            document_id=doc_id,
            document_name=f"{doc_id}.docx",
            source=f"documents/{doc_id}.docx",
            chunk_index=0,
            total_chunks=1,
            content=content,
        ),
        embedding=embedding,
    )


@pytest.mark.integration
class TestChromaVectorStore:
    def test_upsert_search_and_similarity(self, tmp_path: Path) -> None:
        store = ChromaVectorStore(persist_path=tmp_path / "chroma")
        store.upsert(
            [
                _record("c1", "doc1", "copago de imágenes diagnósticas", [1.0, 0.0, 0.0]),
                _record("c2", "doc2", "periodos de carencia del plan", [0.0, 1.0, 0.0]),
            ]
        )
        assert store.count() == 2

        results = store.search([1.0, 0.0, 0.0], top_k=2)
        assert results[0].chunk_id == "c1"
        assert results[0].similarity is not None
        assert results[0].similarity > results[1].similarity  # type: ignore[operator]
        assert results[0].document_name == "doc1.docx"

    def test_delete_document_removes_its_chunks(self, tmp_path: Path) -> None:
        store = ChromaVectorStore(persist_path=tmp_path / "chroma")
        store.upsert(
            [
                _record("c1", "doc1", "contenido uno", [1.0, 0.0]),
                _record("c2", "doc2", "contenido dos", [0.0, 1.0]),
            ]
        )
        store.delete_document("doc1")
        assert store.count() == 1
        remaining = store.search([1.0, 0.0], top_k=5)
        assert {c.document_id for c in remaining} == {"doc2"}

    def test_persistence_across_instances(self, tmp_path: Path) -> None:
        path = tmp_path / "chroma"
        ChromaVectorStore(persist_path=path).upsert(
            [_record("c1", "doc1", "persistente", [0.5, 0.5])]
        )
        assert ChromaVectorStore(persist_path=path).count() == 1
