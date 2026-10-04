"""Pruebas del caso de uso AnalyzeCoverageUseCase (Fase 5, §11.11)."""

import json
from datetime import date

import pytest
from app.application.dto.coverage import CoverageQuery
from app.application.reasoning.evidence_evaluator import EvidenceEvaluator
from app.application.reasoning.knowledge_retriever import KnowledgeRetriever
from app.application.reasoning.reasoning_engine import ReasoningEngine
from app.application.reasoning.response_validator import ResponseValidator
from app.application.use_cases.analyze_coverage_use_case import AnalyzeCoverageUseCase
from app.domain.exceptions.errors import AffiliateNotFoundError, ResponseValidationError
from app.domain.providers.vector_store import VectorRecord
from app.domain.services.eligibility_rules import EligibilityRules
from app.domain.value_objects.document_chunk import DocumentChunk
from app.domain.value_objects.enums import (
    AffiliationStatus,
    CoverageStatus,
    EvidenceStrength,
)

from tests.fixtures.affiliates import make_affiliate
from tests.mocks.in_memory import (
    DeterministicEmbeddingProvider,
    InMemoryAffiliateRepository,
    InMemoryVectorStore,
    StubLLMProvider,
)

TODAY = date(2026, 6, 30)
QUESTION = "¿Está cubierta la resonancia magnética lumbar por mi plan?"


def _valid_llm_reply(chunk_id: str) -> str:
    return json.dumps(
        {
            "status": "APPROVED",
            "summary": "La solicitud procede.",
            "reasoning": "El plan cubre imágenes diagnósticas según la evidencia.",
            "citations": [chunk_id],
            "warnings": [],
        }
    )


def _build_use_case(
    *,
    llm_reply: str,
    with_evidence: bool = True,
    affiliate_status: AffiliationStatus = AffiliationStatus.ACTIVE,
) -> tuple[AnalyzeCoverageUseCase, StubLLMProvider, InMemoryVectorStore]:
    provider = DeterministicEmbeddingProvider()
    store = InMemoryVectorStore()
    if with_evidence:
        content = "cubierta resonancia magnética lumbar por plan con carencia de 6 meses"
        store.upsert(
            [
                VectorRecord(
                    chunk=DocumentChunk(
                        chunk_id="doc2_00001",
                        document_id="doc2",
                        document_name="DOC2.docx",
                        source="documents/DOC2.docx",
                        chunk_index=1,
                        total_chunks=5,
                        content=content,
                    ),
                    embedding=provider.embed_query(content),
                ),
                VectorRecord(
                    chunk=DocumentChunk(
                        chunk_id="doc2_00002",
                        document_id="doc2",
                        document_name="DOC2.docx",
                        source="documents/DOC2.docx",
                        chunk_index=2,
                        total_chunks=5,
                        content="resonancia magnética lumbar cubierta para plan Esencial",
                    ),
                    embedding=provider.embed_query(
                        "resonancia magnética lumbar cubierta para plan Esencial"
                    ),
                ),
            ]
        )
    affiliate = make_affiliate(affiliation_status=affiliate_status)
    engine = ReasoningEngine(
        affiliate_repository=InMemoryAffiliateRepository([affiliate]),
        eligibility_rules=EligibilityRules(),
        retriever=KnowledgeRetriever(
            embedding_provider=provider, vector_store=store, top_k=5, min_similarity=0.2
        ),
        evidence_evaluator=EvidenceEvaluator(),
    )
    llm = StubLLMProvider(reply=llm_reply)
    use_case = AnalyzeCoverageUseCase(
        reasoning_engine=engine, llm_provider=llm, response_validator=ResponseValidator()
    )
    return use_case, llm, store


@pytest.mark.unit
class TestAnalyzeCoverageUseCase:
    def test_happy_path_returns_structured_response(self) -> None:
        use_case, llm, _ = _build_use_case(llm_reply=_valid_llm_reply("doc2_00001"))
        response = use_case.execute(
            CoverageQuery(affiliate_id="A-00001", question=QUESTION), reference=TODAY
        )
        assert response.status is CoverageStatus.APPROVED
        assert response.evidence[0].chunk_id == "doc2_00001"
        assert response.evidence_strength in (EvidenceStrength.PARTIAL, EvidenceStrength.STRONG)
        assert response.trace.trace_id
        assert response.trace.prompt_version == "1.0"
        assert len(llm.requests) == 1  # exactamente UNA llamada (§14.6)

    def test_insufficient_evidence_short_circuits_without_llm(self) -> None:
        use_case, llm, _ = _build_use_case(llm_reply=_valid_llm_reply("x"), with_evidence=False)
        response = use_case.execute(
            CoverageQuery(affiliate_id="A-00001", question=QUESTION), reference=TODAY
        )
        assert response.status is CoverageStatus.INSUFFICIENT_INFORMATION
        assert response.evidence_strength is EvidenceStrength.INSUFFICIENT
        assert not response.evidence
        assert llm.requests == []  # el LLM nunca se invoca sin evidencia (§7.19)

    def test_unknown_affiliate_raises(self) -> None:
        use_case, _, _ = _build_use_case(llm_reply=_valid_llm_reply("doc2_00001"))
        with pytest.raises(AffiliateNotFoundError):
            use_case.execute(
                CoverageQuery(affiliate_id="A-99999", question=QUESTION), reference=TODAY
            )

    def test_blocking_findings_appear_as_warnings(self) -> None:
        use_case, _, _ = _build_use_case(
            llm_reply=_valid_llm_reply("doc2_00001"),
            affiliate_status=AffiliationStatus.WITHDRAWN,
        )
        response = use_case.execute(
            CoverageQuery(affiliate_id="A-00001", question=QUESTION), reference=TODAY
        )
        assert any("no está activo" in w for w in response.warnings)

    def test_invalid_llm_response_raises_controlled_error(self) -> None:
        use_case, _, _ = _build_use_case(llm_reply="respuesta no estructurada")
        with pytest.raises(ResponseValidationError):
            use_case.execute(
                CoverageQuery(affiliate_id="A-00001", question=QUESTION), reference=TODAY
            )

    def test_hallucinated_citation_raises(self) -> None:
        use_case, _, _ = _build_use_case(llm_reply=_valid_llm_reply("chunk_inventado"))
        with pytest.raises(ResponseValidationError):
            use_case.execute(
                CoverageQuery(affiliate_id="A-00001", question=QUESTION), reference=TODAY
            )
