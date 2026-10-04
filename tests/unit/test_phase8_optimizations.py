"""Pruebas de las optimizaciones de Fase 8 (§8.13, §9.12)."""

import pytest
from app.application.reasoning.knowledge_retriever import KnowledgeRetriever
from app.domain.exceptions.errors import ResponseValidationError
from app.domain.value_objects.document_chunk import DocumentChunk

from tests.unit.test_analyze_coverage_use_case import (
    QUESTION,
    TODAY,
    _build_use_case,
    _valid_llm_reply,
)


def _chunk(chunk_id: str, content: str, similarity: float) -> DocumentChunk:
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
class TestContextDeduplication:
    def test_duplicate_content_removed_keeping_most_relevant(self) -> None:
        chunks = [
            _chunk("c1", "La carencia es de 6 meses.", 0.9),
            _chunk("c2", "la carencia   es de 6 meses.", 0.7),  # duplicado normalizado
            _chunk("c3", "Las exclusiones aplican siempre.", 0.6),
        ]
        result = KnowledgeRetriever._deduplicate(chunks)
        assert [c.chunk_id for c in result] == ["c1", "c3"]


@pytest.mark.unit
class TestLLMRetryOnInvalidResponse:
    def test_retries_once_and_succeeds(self) -> None:
        from app.application.dto.coverage import CoverageQuery

        from tests.mocks.in_memory import StubLLMProvider

        use_case, _, _ = _build_use_case(llm_reply="ignored")
        llm = StubLLMProvider(replies=["no es json", _valid_llm_reply("doc2_00001")])
        use_case._llm_provider = llm  # type: ignore[attr-defined]
        response = use_case.execute(
            CoverageQuery(affiliate_id="A-00001", question=QUESTION), reference=TODAY
        )
        assert response.status.value == "APPROVED"
        assert len(llm.requests) == 2  # reintento único

    def test_fails_after_second_invalid_response(self) -> None:
        from app.application.dto.coverage import CoverageQuery

        from tests.mocks.in_memory import StubLLMProvider

        use_case, _, _ = _build_use_case(llm_reply="ignored")
        llm = StubLLMProvider(replies=["no es json", "tampoco es json"])
        use_case._llm_provider = llm  # type: ignore[attr-defined]
        with pytest.raises(ResponseValidationError):
            use_case.execute(
                CoverageQuery(affiliate_id="A-00001", question=QUESTION), reference=TODAY
            )
        assert len(llm.requests) == 2  # nunca más de un reintento
