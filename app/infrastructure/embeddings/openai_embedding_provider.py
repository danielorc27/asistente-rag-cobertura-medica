"""Adapter de embeddings sobre el SDK de OpenAI (§3.6, §14.12)."""

import logging
from collections.abc import Sequence
from typing import Any

from openai import APIError, OpenAI

from app.domain.exceptions.errors import EmbeddingProviderError
from app.domain.providers.embedding_provider import EmbeddingProvider

logger = logging.getLogger(__name__)

_BATCH_SIZE = 100


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Implementación de EmbeddingProvider con batching de chunks."""

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
        base_url: str = "",
        client: Any | None = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        # base_url: endpoints compatibles con OpenAI (Ollama, Gemini, Azure).
        self._base_url = base_url or None
        # Cliente lazy: la app debe poder arrancar sin API Key (§9.12).
        self._client_instance = client

    @property
    def _client(self) -> Any:
        if self._client_instance is None:
            self._client_instance = OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout_seconds,
                max_retries=self._max_retries,
            )
        return self._client_instance

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        embeddings: list[list[float]] = []
        for start in range(0, len(texts), _BATCH_SIZE):
            batch = list(texts[start : start + _BATCH_SIZE])
            embeddings.extend(self._embed_batch(batch))
        logger.info("Embeddings generados: %d (modelo=%s).", len(embeddings), self._model)
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        return self._embed_batch([text])[0]

    def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        if not batch:
            return []
        try:
            response = self._client.embeddings.create(model=self._model, input=batch)
        except APIError as exc:
            raise EmbeddingProviderError(f"Fallo al generar embeddings: {exc}") from exc
        except Exception as exc:
            raise EmbeddingProviderError(f"Error de comunicación con embeddings: {exc}") from exc
        data = list(response.data)
        # OpenAI puebla `index`; algunos endpoints compatibles (p. ej. Gemini)
        # lo devuelven None — en ese caso se preserva el orden de la respuesta,
        # que por contrato de la API corresponde al orden del input (§8.17).
        if all(item.index is not None for item in data):
            data.sort(key=lambda item: item.index)
        return [item.embedding for item in data]
