"""Contrato de la estrategia de fragmentación (§3.5)."""

from abc import ABC, abstractmethod


class ChunkStrategy(ABC):
    """Puerto de fragmentación de texto en chunks con contexto preservado."""

    @abstractmethod
    def split(self, text: str) -> list[str]:
        """Divide el texto en fragmentos según la estrategia configurada.

        Nunca divide palabras y procura mantener coherencia semántica (§6.9).
        """
