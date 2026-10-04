"""Embeddings simulados para modo demo/offline (EMBEDDING_PROVIDER=mock).

Vectores deterministas por bolsa de palabras con hash md5: el retrieval
funciona por solapamiento léxico (suficiente para demos en español),
sin red y de forma reproducible entre procesos.
"""

import hashlib
import math
from collections.abc import Sequence

from app.domain.providers.embedding_provider import EmbeddingProvider

_DIMENSIONS = 256


class MockEmbeddingProvider(EmbeddingProvider):
    """Implementación offline determinista de EmbeddingProvider."""

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._vector(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

    @staticmethod
    def _vector(text: str) -> list[float]:
        vector = [0.0] * _DIMENSIONS
        for token in text.lower().split():
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            vector[int(digest, 16) % _DIMENSIONS] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]
