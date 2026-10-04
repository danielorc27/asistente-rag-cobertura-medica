"""Response Validator (§7.12, §14.15).

Validaciones determinísticas de la respuesta del LLM:
formato JSON, campos requeridos, status válido y citas que referencien
únicamente chunks realmente suministrados en el prompt.

La validación semántica con un segundo LLM queda fuera del alcance v1.
"""

import json
import logging
from dataclasses import dataclass

from app.domain.exceptions.errors import ResponseValidationError
from app.domain.value_objects.enums import CoverageStatus

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = ("status", "summary", "reasoning", "citations", "warnings")


@dataclass(frozen=True)
class ParsedLLMResponse:
    """Respuesta del LLM ya validada y tipada."""

    status: CoverageStatus
    summary: str
    reasoning: str
    citations: tuple[str, ...]
    warnings: tuple[str, ...]


class ResponseValidator:
    """Comprueba que la respuesta del modelo sea utilizable y trazable."""

    def validate(self, raw_text: str, allowed_chunk_ids: set[str]) -> ParsedLLMResponse:
        """Valida y estructura la salida del LLM.

        Raises:
            ResponseValidationError: si el formato, el status o las citas
                no cumplen el contrato.
        """
        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ResponseValidationError(f"La respuesta del LLM no es JSON válido: {exc}") from exc
        if not isinstance(payload, dict):
            raise ResponseValidationError("La respuesta del LLM no es un objeto JSON.")

        missing = [key for key in _REQUIRED_KEYS if key not in payload]
        if missing:
            raise ResponseValidationError(f"Faltan campos en la respuesta: {missing}")

        try:
            status = CoverageStatus(str(payload["status"]))
        except ValueError as exc:
            raise ResponseValidationError(f"Status inválido: {payload['status']!r}") from exc

        summary = str(payload["summary"]).strip()
        reasoning = str(payload["reasoning"]).strip()
        if not summary or not reasoning:
            raise ResponseValidationError("summary y reasoning no pueden estar vacíos.")

        citations = payload["citations"]
        warnings = payload["warnings"]
        if not isinstance(citations, list) or not isinstance(warnings, list):
            raise ResponseValidationError("citations y warnings deben ser listas.")
        citation_ids = tuple(str(c) for c in citations)

        unknown = [c for c in citation_ids if c not in allowed_chunk_ids]
        if unknown:
            raise ResponseValidationError(
                f"La respuesta cita chunks no suministrados: {unknown} (§7.14)."
            )
        if status is not CoverageStatus.INSUFFICIENT_INFORMATION and not citation_ids:
            raise ResponseValidationError(
                "Una decisión de cobertura requiere al menos una cita (§7.14)."
            )

        logger.info(
            "Respuesta del LLM validada: status=%s, citas=%d.", status.value, len(citation_ids)
        )
        return ParsedLLMResponse(
            status=status,
            summary=summary,
            reasoning=reasoning,
            citations=citation_ids,
            warnings=tuple(str(w) for w in warnings),
        )
