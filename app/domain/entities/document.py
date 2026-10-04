"""Entidad Documento: modelo uniforme entregado por cualquier DocumentLoader (§3.4)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Document:
    """Documento fuente ya cargado y con texto extraído."""

    document_id: str
    name: str
    source: str
    doc_type: str
    size_bytes: int
    modified_at: datetime
    content: str
    content_hash: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.content.strip()
