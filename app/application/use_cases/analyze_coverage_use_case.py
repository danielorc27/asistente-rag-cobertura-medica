"""Caso de uso principal: análisis de cobertura (§14.2).

Punto de entrada único del flujo de consulta (§7.16):
razonamiento → prompt → UNA llamada al LLM (§14.6) → validación → DTO.

Si la evidencia es INSUFFICIENT no se invoca el LLM: el sistema responde
INSUFFICIENT_INFORMATION de forma determinística (§7.15, §13.4) — nunca
se genera una decisión sin evidencia documental.
"""

import json
import logging
import uuid
from datetime import date

from app.application.dto.coverage import (
    CoverageQuery,
    CoverageResponse,
    CoverageTrace,
    EvidenceItem,
)
from app.application.prompts.coverage_prompt_builder import (
    PROMPT_VERSION,
    CoveragePromptBuilder,
)
from app.application.reasoning.reasoning_engine import ReasoningContext, ReasoningEngine
from app.application.reasoning.response_validator import ResponseValidator
from app.domain.exceptions.errors import ResponseValidationError
from app.domain.providers.llm_provider import LLMProvider
from app.domain.value_objects.enums import CoverageStatus, EvidenceStrength

logger = logging.getLogger(__name__)


class AnalyzeCoverageUseCase:
    """Orquesta el flujo completo de una consulta de cobertura."""

    def __init__(
        self,
        reasoning_engine: ReasoningEngine,
        llm_provider: LLMProvider,
        response_validator: ResponseValidator,
    ) -> None:
        self._reasoning_engine = reasoning_engine
        self._llm_provider = llm_provider
        self._response_validator = response_validator

    def execute(self, query: CoverageQuery, reference: date | None = None) -> CoverageResponse:
        """Analiza la cobertura para la consulta dada.

        Raises:
            AffiliateNotFoundError: si el afiliado no existe.
            LLMProviderError: ante fallos del proveedor LLM.
            ResponseValidationError: si la respuesta del LLM es inválida.
        """
        trace_id = str(uuid.uuid4())
        reference = reference or date.today()
        context = self._reasoning_engine.analyze(query.affiliate_id, query.question, reference)

        if context.evidence_strength is EvidenceStrength.INSUFFICIENT:
            return self._insufficient_evidence_response(trace_id, context)

        request = (
            CoveragePromptBuilder()
            .add_reasoning_instructions()
            .add_evidence_rules()
            .add_affiliate(context.affiliate, context.assessment)
            .add_evidence(context.chunks)
            .add_question(query.question)
            .add_response_format()
            .add_guardrails()
            .build()
        )
        allowed_ids = {chunk.chunk_id for chunk in context.chunks}
        result = self._llm_provider.generate(request)
        try:
            parsed = self._response_validator.validate(result.text, allowed_ids)
        except ResponseValidationError as exc:
            # Recuperación (§9.12): un único reintento ante salida inválida
            # del modelo; si vuelve a fallar, error controlado (§7.12).
            logger.warning("Respuesta LLM inválida (%s); se reintenta una vez.", exc)
            result = self._llm_provider.generate(request)
            parsed = self._response_validator.validate(result.text, allowed_ids)

        cited = {chunk.chunk_id: chunk for chunk in context.chunks}
        evidence = [
            EvidenceItem(
                chunk_id=chunk_id,
                document_name=cited[chunk_id].document_name,
                content=cited[chunk_id].content,
                similarity=cited[chunk_id].similarity,
            )
            for chunk_id in parsed.citations
        ]
        warnings = list(parsed.warnings)
        for finding in context.assessment.blocking_findings:
            if finding.detail not in warnings:
                warnings.append(finding.detail)

        response = CoverageResponse(
            status=parsed.status,
            summary=parsed.summary,
            reasoning=parsed.reasoning,
            evidence=evidence,
            evidence_strength=context.evidence_strength,
            warnings=warnings,
            trace=CoverageTrace(
                trace_id=trace_id,
                model=result.model,
                prompt_version=PROMPT_VERSION,
                latency_ms=result.latency_ms,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                retrieved_chunks=len(context.chunks),
            ),
        )
        self._log_trace(trace_id, query, context, response)
        return response

    def _insufficient_evidence_response(
        self, trace_id: str, context: ReasoningContext
    ) -> CoverageResponse:
        """Respuesta determinística sin LLM cuando no hay evidencia (§7.15)."""
        warnings = [f.detail for f in context.assessment.blocking_findings]
        response = CoverageResponse(
            status=CoverageStatus.INSUFFICIENT_INFORMATION,
            summary="No fue posible encontrar evidencia documental suficiente para la consulta.",
            reasoning=(
                "La búsqueda en la documentación disponible no recuperó fragmentos "
                "relevantes por encima del umbral de similitud configurado. "
                "De acuerdo con el principio de evidencia (§7.14), el sistema no "
                "emite decisiones sin respaldo documental."
            ),
            evidence=[],
            evidence_strength=EvidenceStrength.INSUFFICIENT,
            warnings=warnings,
            trace=CoverageTrace(trace_id=trace_id, retrieved_chunks=len(context.chunks)),
        )
        logger.info("Consulta %s resuelta sin LLM: evidencia insuficiente.", trace_id)
        return response

    def _log_trace(
        self,
        trace_id: str,
        query: CoverageQuery,
        context: ReasoningContext,
        response: CoverageResponse,
    ) -> None:
        """Traza estructurada por consulta (§7.18, §14.13) sin datos personales."""
        logger.info(
            "trace %s",
            json.dumps(
                {
                    "trace_id": trace_id,
                    "affiliate_id": query.affiliate_id,
                    "status": response.status.value,
                    "evidence_strength": response.evidence_strength.value,
                    "chunks": [c.chunk_id for c in context.chunks],
                    "citations": [e.chunk_id for e in response.evidence],
                    "model": response.trace.model,
                    "prompt_version": response.trace.prompt_version,
                    "latency_ms": response.trace.latency_ms,
                },
                ensure_ascii=False,
            ),
        )
