"""Contrato del almacén vectorial (§3.7)."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from app.domain.value_objects.document_chunk import DocumentChunk


@dataclass(frozen=True)
class VectorRecord:
    """Chunk acompañado de su embedding, listo para indexar."""

    chunk: DocumentChunk
    embedding: list[float]


class VectorStore(ABC):
    """Puerto de indexación y búsqueda vectorial."""

    @abstractmethod
    def upsert(self, records: Sequence[VectorRecord]) -> None:
        """Inserta o actualiza chunks con sus embeddings."""

    @abstractmethod
    def search(self, embedding: Sequence[float], top_k: int) -> list[DocumentChunk]:
        """Busca los ``top_k`` chunks más similares, con ``similarity`` poblado."""

    @abstractmethod
    def delete_document(self, document_id: str) -> None:
        """Elimina todos los chunks de un documento (§14.11)."""

    @abstractmethod
    def reset(self) -> None:
        """Vacía el índice por completo (reindexación FULL).

        Debe eliminar también metadatos estructurales como la
        dimensionalidad, que puede cambiar al cambiar de proveedor
        de embeddings.
        """

    @abstractmethod
    def count(self) -> int:
        """Cantidad total de chunks indexados."""
