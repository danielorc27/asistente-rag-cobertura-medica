"""Contrato del proveedor LLM (§3.8, §14.6).

El flujo de consulta realiza exactamente una llamada al LLM. El contrato
transporta metadatos suficientes para trazabilidad (§7.18) y soporta
salida estructurada JSON.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMRequest:
    """Solicitud al modelo, ya construida por el PromptBuilder."""

    system: str
    user: str
    json_output: bool = True


@dataclass(frozen=True)
class LLMResult:
    """Respuesta del modelo con metadatos de trazabilidad."""

    text: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: float | None = None


class LLMProvider(ABC):
    """Puerto del modelo de lenguaje; oculta el SDK del proveedor."""

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResult:
        """Genera una respuesta.

        Raises:
            LLMProviderError: ante fallos de comunicación, timeout o
                respuesta vacía del proveedor.
        """
