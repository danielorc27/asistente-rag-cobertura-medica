"""Reasoning Engine (§7.4, §14.2): sub-orquestador de la etapa de razonamiento.

Obtiene la evidencia y construye el contexto de decisión ANTES del LLM:
afiliado → reglas determinísticas → retrieval → evaluación de evidencia.
No llama al LLM ni construye prompts (§7.2: nunca mezclar obtención de
evidencia con generación de respuestas).
"""

import logging
from dataclasses import dataclass
from datetime import date

from app.application.reasoning.evidence_evaluator import EvidenceEvaluator
from app.application.reasoning.knowledge_retriever import KnowledgeRetriever
from app.domain.entities.affiliate import Affiliate
from app.domain.entities.preliminary_assessment import PreliminaryAssessment
from app.domain.exceptions.errors import AffiliateNotFoundError
from app.domain.repositories.affiliate_repository import AffiliateRepository
from app.domain.services.eligibility_rules import EligibilityRules
from app.domain.value_objects.document_chunk import DocumentChunk
from app.domain.value_objects.enums import EvidenceStrength

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReasoningContext:
    """Insumos completos para la decisión: afiliado + hechos + evidencia."""

    affiliate: Affiliate
    assessment: PreliminaryAssessment
    chunks: list[DocumentChunk]
    evidence_strength: EvidenceStrength


class ReasoningEngine:
    """Coordina la obtención de evidencia y el análisis determinístico."""

    def __init__(
        self,
        affiliate_repository: AffiliateRepository,
        eligibility_rules: EligibilityRules,
        retriever: KnowledgeRetriever,
        evidence_evaluator: EvidenceEvaluator,
    ) -> None:
        self._affiliate_repository = affiliate_repository
        self._eligibility_rules = eligibility_rules
        self._retriever = retriever
        self._evidence_evaluator = evidence_evaluator

    def analyze(self, affiliate_id: str, question: str, reference: date) -> ReasoningContext:
        """Construye el contexto de razonamiento (§7.16).

        Raises:
            AffiliateNotFoundError: si el afiliado no existe.
        """
        affiliate = self._affiliate_repository.find_by_id(affiliate_id)
        if affiliate is None:
            raise AffiliateNotFoundError(affiliate_id)
        logger.info("Afiliado %s resuelto (plan=%s).", affiliate.affiliate_id, affiliate.plan)

        assessment = self._eligibility_rules.evaluate(affiliate, reference)
        chunks = self._retriever.retrieve(question)
        strength = self._evidence_evaluator.evaluate(chunks)
        return ReasoningContext(
            affiliate=affiliate,
            assessment=assessment,
            chunks=chunks,
            evidence_strength=strength,
        )
