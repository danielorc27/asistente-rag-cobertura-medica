"""Evidence Evaluator (§7.8, §14.7).

Deriva EvidenceStrength mediante reglas explícitas sobre los scores de
retrieval. Nunca lo decide el LLM.
"""

import logging

from app.domain.value_objects.document_chunk import DocumentChunk
from app.domain.value_objects.enums import EvidenceStrength
from app.shared.constants.retrieval import STRONG_MIN_CHUNKS, STRONG_TOP_SIMILARITY

logger = logging.getLogger(__name__)


class EvidenceEvaluator:
    """Evalúa la suficiencia de la evidencia recuperada."""

    def evaluate(self, chunks: list[DocumentChunk]) -> EvidenceStrength:
        """Reglas (documentadas en shared/constants/retrieval.py):

        - Sin chunks relevantes → INSUFFICIENT.
        - Mejor similitud ≥ STRONG_TOP_SIMILARITY y al menos
          STRONG_MIN_CHUNKS chunks → STRONG.
        - En cualquier otro caso → PARTIAL.
        """
        if not chunks:
            strength = EvidenceStrength.INSUFFICIENT
        else:
            top = max(c.similarity or 0.0 for c in chunks)
            if top >= STRONG_TOP_SIMILARITY and len(chunks) >= STRONG_MIN_CHUNKS:
                strength = EvidenceStrength.STRONG
            else:
                strength = EvidenceStrength.PARTIAL
        logger.info("Evidencia evaluada: %s (%d chunks).", strength.value, len(chunks))
        return strength
