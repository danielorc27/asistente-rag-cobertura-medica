"""Pruebas de la entidad Document (Fase 2)."""

from datetime import datetime

import pytest
from app.domain.entities.document import Document


def _doc(content: str) -> Document:
    return Document(
        document_id="doc1",
        name="DOC1_Manual_de_Beneficios.docx",
        source="documents/DOC1_Manual_de_Beneficios.docx",
        doc_type="docx",
        size_bytes=1024,
        modified_at=datetime(2026, 6, 1, 12, 0),
        content=content,
        content_hash="abc123",
    )


@pytest.mark.unit
class TestDocument:
    def test_non_empty_document(self) -> None:
        doc = _doc("Contenido del manual.")
        assert not doc.is_empty
        assert doc.content_hash == "abc123"

    def test_empty_and_whitespace_document(self) -> None:
        assert _doc("").is_empty
        assert _doc("   \n\t  ").is_empty
