"""Dobles de prueba en memoria para los contratos del dominio (§11.4)."""

import hashlib
import math
from collections.abc import Sequence

from app.domain.entities.affiliate import Affiliate
from app.domain.providers.embedding_provider import EmbeddingProvider
from app.domain.providers.llm_provider import LLMProvider, LLMRequest, LLMResult
from app.domain.providers.vector_store import VectorRecord, VectorStore
from app.domain.repositories.affiliate_repository import AffiliateRepository
from app.domain.repositories.index_state_repository import IndexManifest, IndexStateRepository
from app.domain.value_objects.document_chunk import DocumentChunk


class InMemoryVectorStore(VectorStore):
    """VectorStore en memoria con similitud coseno real."""

    def __init__(self) -> None:
        self.records: dict[str, VectorRecord] = {}

    def upsert(self, records: Sequence[VectorRecord]) -> None:
        for record in records:
            self.records[record.chunk.chunk_id] = record

    def search(self, embedding: Sequence[float], top_k: int) -> list[DocumentChunk]:
        scored = [(self._cosine(embedding, r.embedding), r.chunk) for r in self.records.values()]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk.with_similarity(score) for score, chunk in scored[:top_k]]

    def delete_document(self, document_id: str) -> None:
        self.records = {
            cid: r for cid, r in self.records.items() if r.chunk.document_id != document_id
        }

    def reset(self) -> None:
        self.records = {}

    def count(self) -> int:
        return len(self.records)

    @staticmethod
    def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b, strict=False))
        norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
        return dot / norm if norm else 0.0


class InMemoryIndexStateRepository(IndexStateRepository):
    def __init__(self) -> None:
        self.manifest: IndexManifest | None = None

    def load(self) -> IndexManifest | None:
        return self.manifest

    def save(self, manifest: IndexManifest) -> None:
        self.manifest = manifest


class DeterministicEmbeddingProvider(EmbeddingProvider):
    """Embeddings deterministas basados en hash md5 de tokens (sin red).

    Se usa md5 (no ``hash()``) porque este último se aleatoriza por proceso
    y produciría pruebas no reproducibles.
    """

    def __init__(self, dimensions: int = 64) -> None:
        self._dimensions = dimensions
        self.texts_embedded: list[str] = []

    def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        self.texts_embedded.extend(texts)
        return [self._vector(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vector(text)

    def _vector(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        for token in text.lower().split():
            digest = hashlib.md5(token.encode("utf-8")).hexdigest()
            vector[int(digest, 16) % self._dimensions] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class StubLLMProvider(LLMProvider):
    """LLM simulado que registra requests.

    ``reply`` fija una respuesta única; ``replies`` entrega una secuencia
    (la última se repite si se agota) para probar reintentos.
    """

    def __init__(self, reply: str = "", replies: Sequence[str] | None = None) -> None:
        self._replies = list(replies) if replies is not None else [reply]
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResult:
        self.requests.append(request)
        index = min(len(self.requests) - 1, len(self._replies) - 1)
        return LLMResult(
            text=self._replies[index],
            model="stub",
            input_tokens=10,
            output_tokens=10,
            latency_ms=1.0,
        )


class InMemoryAffiliateRepository(AffiliateRepository):
    def __init__(self, affiliates: Sequence[Affiliate] = ()) -> None:
        self._by_id = {a.affiliate_id: a for a in affiliates}

    def find_by_id(self, affiliate_id: str) -> Affiliate | None:
        return self._by_id.get(affiliate_id.strip())
