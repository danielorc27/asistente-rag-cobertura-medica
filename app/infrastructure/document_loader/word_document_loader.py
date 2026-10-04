"""Loader de documentos Word (§3.4, §5.9).

Extrae párrafos y tablas EN ORDEN DE APARICIÓN. Las tablas son críticas:
DOC1 y DOC2 contienen los esquemas de copagos y carencias en tablas; un
extractor solo de párrafos perdería la información de cobertura.
"""

import logging
from datetime import datetime
from pathlib import Path

from docx import Document as DocxReader
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.domain.entities.document import Document
from app.domain.exceptions.errors import DocumentLoadError
from app.domain.providers.document_loader import DocumentLoader

logger = logging.getLogger(__name__)

_HEADING_PREFIXES = {1: "# ", 2: "## ", 3: "### "}


class WordDocumentLoader(DocumentLoader):
    """Implementación de DocumentLoader para archivos .docx."""

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".docx" and not path.name.startswith("~$")

    def load(self, path: Path) -> Document:
        if not path.exists():
            raise DocumentLoadError(f"El archivo no existe: {path}")
        try:
            docx = DocxReader(str(path))
        except Exception as exc:  # python-docx lanza excepciones heterogéneas
            raise DocumentLoadError(f"No fue posible abrir '{path.name}': {exc}") from exc

        blocks: list[str] = []
        for element in docx.element.body.iterchildren():
            if element.tag == qn("w:p"):
                text = self._render_paragraph(Paragraph(element, docx))
                if text:
                    blocks.append(text)
            elif element.tag == qn("w:tbl"):
                text = self._render_table(Table(element, docx))
                if text:
                    blocks.append(text)

        stat = path.stat()
        content = "\n\n".join(blocks)
        logger.info(
            "Documento '%s' cargado: %d bloques, %d caracteres.",
            path.name,
            len(blocks),
            len(content),
        )
        return Document(
            document_id=path.stem.lower(),
            name=path.name,
            source=str(path),
            doc_type="docx",
            size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            content=content,
        )

    def _render_paragraph(self, paragraph: Paragraph) -> str:
        text = paragraph.text.strip()
        if not text:
            return ""
        style = (paragraph.style.name or "") if paragraph.style else ""
        if style.startswith("Heading"):
            try:
                level = int(style.removeprefix("Heading ").strip() or "1")
            except ValueError:
                level = 1
            return _HEADING_PREFIXES.get(level, "### ") + text
        return text

    def _render_table(self, table: Table) -> str:
        """Serializa la tabla como filas 'celda | celda | ...' legibles por el LLM."""
        rows: list[str] = []
        for row in table.rows:
            cells = [" ".join(cell.text.split()) for cell in row.cells]
            if any(cells):
                rows.append(" | ".join(cells))
        return "\n".join(rows)
