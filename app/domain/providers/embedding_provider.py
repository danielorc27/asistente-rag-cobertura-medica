"""Contrato del generador de embeddings (§3.6, §14.12)."""

from abc import ABC, abstractmethod
from collections.abc import Sequence


class EmbeddingProvider(ABC):
    """Puerto de generación de embeddings; oculta el SDK utilizado."""

    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Genera un embedding por texto (batching permitido y deseable).

        Raises:
            EmbeddingProviderError: ante fallos del proveedor.
        """

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Genera el embedding de una consulta individual."""
