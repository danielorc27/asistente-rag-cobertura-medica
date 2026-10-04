"""Contrato de normalización de texto (§6.6)."""

from abc import ABC, abstractmethod


class TextNormalizer(ABC):
    """Puerto de limpieza de texto; nunca modifica el significado."""

    @abstractmethod
    def normalize(self, text: str) -> str:
        """Elimina espacios múltiples, saltos y caracteres invisibles."""
