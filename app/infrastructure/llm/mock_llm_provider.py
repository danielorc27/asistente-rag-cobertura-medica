"""Proveedor LLM simulado para modo demo/offline (LLM_PROVIDER=mock).

Permite ejecutar el sistema completo (ingesta + API) sin ningún servicio
externo. Toda respuesta queda marcada explícitamente como SIMULADA y usa
status INSUFFICIENT_INFORMATION: el mock demuestra el pipeline y el
retrieval, nunca fabrica una decisión de cobertura (§13.2).
"""

import json
import logging
import re

from app.domain.providers.llm_provider import LLMProvider, LLMRequest, LLMResult

logger = logging.getLogger(__name__)

_CHUNK_ID_PATTERN = re.compile(r"\[([a-z0-9_]+_\d{5})\]")


class MockLLMProvider(LLMProvider):
    """Genera una respuesta JSON válida citando los chunks del prompt."""

    def generate(self, request: LLMRequest) -> LLMResult:
        chunk_ids = _CHUNK_ID_PATTERN.findall(request.user)
        documents = sorted(set(re.findall(r"fuente: ([^)]+)\)", request.user)))
        payload = {
            "status": "INSUFFICIENT_INFORMATION",
            "summary": (
                "[RESPUESTA SIMULADA - MockLLMProvider] El sistema opera en modo "
                "demo sin un modelo de lenguaje real; no es posible emitir una "
                "decisión de cobertura."
            ),
            "reasoning": (
                "Modo demo: el pipeline completo se ejecutó correctamente "
                f"(retrieval recuperó {len(chunk_ids)} fragmentos de: "
                f"{', '.join(documents) if documents else 'ningún documento'}). "
                "Configure un proveedor LLM real (LLM_PROVIDER=openai con "
                "OPENAI_BASE_URL opcional) para obtener el análisis."
            ),
            "citations": chunk_ids,
            "warnings": ["Respuesta generada por MockLLMProvider: solo para demostración."],
        }
        logger.info("MockLLMProvider respondió citando %d chunks.", len(chunk_ids))
        return LLMResult(
            text=json.dumps(payload, ensure_ascii=False),
            model="mock-llm",
            input_tokens=0,
            output_tokens=0,
            latency_ms=0.0,
        )
