"""Pruebas del Prompt Builder (Fase 5, §11.12)."""

from datetime import date

import pytest
from app.application.prompts.coverage_prompt_builder import CoveragePromptBuilder
from app.domain.services.eligibility_rules import EligibilityRules
from app.domain.value_objects.document_chunk import DocumentChunk

from tests.fixtures.affiliates import make_affiliate


def _chunk(chunk_id: str, content: str) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc2",
        document_name="DOC2_Terminos.docx",
        source="documents/DOC2.docx",
        chunk_index=3,
        total_chunks=10,
        content=content,
    )


@pytest.mark.unit
class TestCoveragePromptBuilder:
    def _build(self) -> tuple[str, str]:
        affiliate = make_affiliate(plan="Premium", tenure_months=14)
        assessment = EligibilityRules().evaluate(affiliate, date(2026, 6, 30))
        request = (
            CoveragePromptBuilder()
            .add_reasoning_instructions()
            .add_evidence_rules()
            .add_affiliate(affiliate, assessment)
            .add_evidence([_chunk("doc2_00003", "La carencia para imágenes es de 6 meses.")])
            .add_question("¿Está cubierta la resonancia lumbar?")
            .add_response_format()
            .add_guardrails()
            .build()
        )
        return request.system, request.user

    def test_contains_affiliate_business_data(self) -> None:
        _, user = self._build()
        assert "Premium" in user
        assert "14 meses" in user
        assert "A-00001" in user

    def test_never_contains_personal_identifiers(self) -> None:
        """§9.18: el prompt no transporta nombre ni documento del afiliado."""
        system, user = self._build()
        full = system + user
        assert "Prueba" not in full  # nombre
        assert "1000000000" not in full  # número de documento
        assert "prueba@ejemplo.com" not in full
        assert "3000000000" not in full

    def test_contains_evidence_with_chunk_ids(self) -> None:
        _, user = self._build()
        assert "doc2_00003" in user
        assert "La carencia para imágenes es de 6 meses." in user

    def test_contains_question_format_and_guardrails(self) -> None:
        _, user = self._build()
        assert "¿Está cubierta la resonancia lumbar?" in user
        assert "INSUFFICIENT_INFORMATION" in user
        assert "No inventes información" in user

    def test_json_output_enabled(self) -> None:
        affiliate = make_affiliate()
        assessment = EligibilityRules().evaluate(affiliate, date(2026, 6, 30))
        request = CoveragePromptBuilder().add_affiliate(affiliate, assessment).build()
        assert request.json_output
        assert request.system
