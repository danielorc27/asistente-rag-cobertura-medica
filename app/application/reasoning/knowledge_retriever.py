"""Knowledge Retriever (§7.7): recupera evidencia documental.

Nunca responde preguntas ni genera texto. Filtra por umbral de relevancia
(§14.10): un chunk bajo el umbral no constituye evidencia.
"""

import logging

from app.domain.providers.embedding_provider import EmbeddingProvider
from app.domain.providers.vector_store import VectorStore
from app.domain.value_objects.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """Recupera los chunks relevantes para una consulta."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        top_k: int,
        min_similarity: float,
    ) -> None:
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._top_k = top_k
        self._min_similarity = min_similarity

    def retrieve(self, query: str) -> list[DocumentChunk]:
        """Busca evidencia; devuelve solo chunks sobre el umbral (§14.10).

        Optimización de contexto (§8.13): elimina chunks con contenido
        duplicado preservando el de mayor relevancia — maximiza la
        relación señal/ruido enviada al modelo.
        """
        embedding = self._embedding_provider.embed_query(query)
        candidates = self._vector_store.search(embedding, top_k=self._top_k)
        relevant = [
            chunk
            for chunk in candidates
            if chunk.similarity is not None and chunk.similarity >= self._min_similarity
        ]
        deduplicated = self._deduplicate(relevant)
        logger.info(
            "Retrieval: %d candidatos, %d sobre el umbral %.2f, %d tras deduplicar.",
            len(candidates),
            len(relevant),
            self._min_similarity,
            len(deduplicated),
        )
        return deduplicated

    @staticmethod
    def _deduplicate(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        """Descarta contenido repetido; conserva el primer (más relevante)."""
        seen: set[str] = set()
        unique: list[DocumentChunk] = []
        for chunk in chunks:
            fingerprint = " ".join(chunk.content.lower().split())
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique.append(chunk)
        return unique
