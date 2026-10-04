"""Contrato de persistencia del manifiesto del índice vectorial (§14.11)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class IndexManifest:
    """Estado del índice: parámetros de construcción y hashes por documento.

    Si los parámetros no coinciden con la configuración actual, el índice
    se considera inválido y requiere reindexación FULL.
    """

    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    pipeline_version: str
    documents: dict[str, str] = field(default_factory=dict)  # nombre -> hash

    def is_compatible_with(self, embedding_model: str, chunk_size: int, chunk_overlap: int) -> bool:
        return (
            self.embedding_model == embedding_model
            and self.chunk_size == chunk_size
            and self.chunk_overlap == chunk_overlap
        )


class IndexStateRepository(ABC):
    """Puerto de lectura/escritura del manifiesto del índice."""

    @abstractmethod
    def load(self) -> IndexManifest | None:
        """Devuelve el manifiesto persistido, o ``None`` si no existe."""

    @abstractmethod
    def save(self, manifest: IndexManifest) -> None:
        """Persiste el manifiesto de forma atómica."""
