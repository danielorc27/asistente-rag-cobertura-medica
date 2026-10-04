"""Pruebas del retriever y el evaluador de evidencia (Fase 5, §11.10)."""

import pytest
from app.application.reasoning.evidence_evaluator import EvidenceEvaluator
from app.application.reasoning.knowledge_retriever import KnowledgeRetriever
from app.domain.providers.vector_store import VectorRecord
from app.domain.value_objects.document_chunk import DocumentChunk
from app.domain.value_objects.enums import EvidenceStrength

from tests.mocks.in_memory import DeterministicEmbeddingProvider, InMemoryVectorStore


def _chunk(chunk_id: str, content: str, similarity: float | None = None) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc",
        document_name="doc.docx",
        source="documents/doc.docx",
        chunk_index=0,
        total_chunks=1,
        content=content,
        similarity=similarity,
    )


@pytest.mark.unit
class TestKnowledgeRetriever:
    def test_filters_chunks_below_threshold(self) -> None:
        provider = DeterministicEmbeddingProvider()
        store = InMemoryVectorStore()
        store.upsert(
            [
                VectorRecord(
                    chunk=_chunk("c1", "resonancia magnética lumbar cobertura"),
                    embedding=provider.embed_query("resonancia magnética lumbar cobertura"),
                ),
                VectorRecord(
                    chunk=_chunk("c2", "zzz tema totalmente distinto qqq"),
                    embedding=provider.embed_query("zzz tema totalmente distinto qqq"),
                ),
            ]
        )
        retriever = KnowledgeRetriever(
            embedding_provider=provider, vector_store=store, top_k=5, min_similarity=0.6
        )
        results = retriever.retrieve("cobertura resonancia magnética lumbar")
        assert [c.chunk_id for c in results] == ["c1"]

    def test_returns_empty_when_nothing_relevant(self) -> None:
        retriever = KnowledgeRetriever(
            embedding_provider=DeterministicEmbeddingProvider(),
            vector_store=InMemoryVectorStore(),
            top_k=5,
            min_similarity=0.25,
        )
        assert retriever.retrieve("cualquier consulta") == []


@pytest.mark.unit
class TestEvidenceEvaluator:
    def setup_method(self) -> None:
        self.evaluator = EvidenceEvaluator()

    def test_no_chunks_is_insufficient(self) -> None:
        assert self.evaluator.evaluate([]) is EvidenceStrength.INSUFFICIENT

    def test_high_similarity_multiple_chunks_is_strong(self) -> None:
        chunks = [_chunk("c1", "a", 0.8), _chunk("c2", "b", 0.5)]
        assert self.evaluator.evaluate(chunks) is EvidenceStrength.STRONG

    def test_single_chunk_is_partial(self) -> None:
        assert self.evaluator.evaluate([_chunk("c1", "a", 0.9)]) is EvidenceStrength.PARTIAL

    def test_low_similarity_is_partial(self) -> None:
        chunks = [_chunk("c1", "a", 0.3), _chunk("c2", "b", 0.28)]
        assert self.evaluator.evaluate(chunks) is EvidenceStrength.PARTIAL
