"""Pruebas de integración del WordDocumentLoader contra los documentos reales."""

from pathlib import Path

import pytest
from app.domain.exceptions.errors import DocumentLoadError
from app.infrastructure.document_loader.word_document_loader import WordDocumentLoader

DOCUMENTS = Path(__file__).resolve().parents[2] / "documents"


@pytest.mark.integration
class TestWordDocumentLoader:
    def setup_method(self) -> None:
        self.loader = WordDocumentLoader()

    def test_supports_only_docx(self) -> None:
        assert self.loader.supports(Path("a.docx"))
        assert self.loader.supports(Path("A.DOCX"))
        assert not self.loader.supports(Path("a.pdf"))
        assert not self.loader.supports(Path("~$temporal.docx"))

    def test_loads_real_manual(self) -> None:
        doc = self.loader.load(DOCUMENTS / "DOC1_Manual_de_Beneficios.docx")
        assert not doc.is_empty
        assert doc.doc_type == "docx"
        assert doc.document_id == "doc1_manual_de_beneficios"
        assert "# 1. Objeto y alcance" in doc.content

    def test_extracts_tables_from_manual(self) -> None:
        """DOC1 contiene los copagos en tablas; deben sobrevivir a la extracción."""
        doc = self.loader.load(DOCUMENTS / "DOC1_Manual_de_Beneficios.docx")
        table_lines = [line for line in doc.content.splitlines() if " | " in line]
        assert len(table_lines) >= 5, "Las tablas del manual no fueron extraídas"

    def test_missing_file_raises_domain_error(self) -> None:
        with pytest.raises(DocumentLoadError):
            self.loader.load(DOCUMENTS / "NO_EXISTE.docx")
