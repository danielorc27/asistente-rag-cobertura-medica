"""Contrato de carga de documentos (§3.4)."""

from abc import ABC, abstractmethod
from pathlib import Path

from app.domain.entities.document import Document


class DocumentLoader(ABC):
    """Puerto de lectura de documentos; entrega un modelo uniforme.

    Solo abre el archivo, extrae texto y metadatos básicos. Nunca
    interpreta contenido, genera embeddings ni realiza chunking (§6.5).
    """

    @abstractmethod
    def supports(self, path: Path) -> bool:
        """Indica si este loader puede procesar el archivo dado."""

    @abstractmethod
    def load(self, path: Path) -> Document:
        """Carga el documento y extrae su texto.

        Raises:
            DocumentLoadError: si el archivo no puede leerse.
        """
