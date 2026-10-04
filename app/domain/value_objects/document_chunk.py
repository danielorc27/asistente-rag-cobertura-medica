"""Fragmento documental recuperable, con trazabilidad completa (§6.10)."""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class DocumentChunk:
    """Fragmento de un documento indexado.

    ``similarity`` solo está presente cuando el chunk proviene de una
    búsqueda vectorial (0..1, mayor es más relevante).
    """

    chunk_id: str
    document_id: str
    document_name: str
    source: str
    chunk_index: int
    total_chunks: int
    content: str
    similarity: float | None = None

    def with_similarity(self, similarity: float) -> "DocumentChunk":
        """Copia inmutable del chunk con el score de la búsqueda."""
        return replace(self, similarity=similarity)
