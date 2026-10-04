"""Adapter del almacén vectorial sobre ChromaDB (§3.7, §5.8).

Persistencia local en VECTOR_DB_PATH con distancia coseno; la similitud
expuesta al dominio es ``1 - distancia`` (0..1, mayor es más relevante).
"""

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import chromadb

from app.domain.providers.vector_store import VectorRecord, VectorStore
from app.domain.value_objects.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)

_COLLECTION = "coverage_documents"


class ChromaVectorStore(VectorStore):
    """Implementación de VectorStore sobre ChromaDB persistente."""

    def __init__(self, persist_path: Path) -> None:
        persist_path.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_path))
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION, metadata={"hnsw:space": "cosine"}
        )

    def reset(self) -> None:
        """Recrea la colección: borra vectores y su dimensionalidad."""
        self._client.delete_collection(_COLLECTION)
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION, metadata={"hnsw:space": "cosine"}
        )
        logger.info("Vector store: colección reiniciada.")

    def upsert(self, records: Sequence[VectorRecord]) -> None:
        if not records:
            return
        self._collection.upsert(
            ids=[r.chunk.chunk_id for r in records],
            embeddings=cast("Any", [r.embedding for r in records]),
            documents=[r.chunk.content for r in records],
            metadatas=[
                {
                    "document_id": r.chunk.document_id,
                    "document_name": r.chunk.document_name,
                    "source": r.chunk.source,
                    "chunk_index": r.chunk.chunk_index,
                    "total_chunks": r.chunk.total_chunks,
                }
                for r in records
            ],
        )
        logger.info("Vector store: upsert de %d chunks.", len(records))

    def search(self, embedding: Sequence[float], top_k: int) -> list[DocumentChunk]:
        result = self._collection.query(
            query_embeddings=cast("Any", [list(embedding)]),
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        ids = result["ids"][0] if result["ids"] else []
        documents = result["documents"][0] if result["documents"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        distances = result["distances"][0] if result["distances"] else []

        chunks: list[DocumentChunk] = []
        for chunk_id, content, meta, distance in zip(
            ids, documents, metadatas, distances, strict=True
        ):
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=str(meta["document_id"]),
                    document_name=str(meta["document_name"]),
                    source=str(meta["source"]),
                    chunk_index=int(str(meta["chunk_index"])),
                    total_chunks=int(str(meta["total_chunks"])),
                    content=content,
                    similarity=max(0.0, 1.0 - float(distance)),
                )
            )
        return chunks

    def delete_document(self, document_id: str) -> None:
        self._collection.delete(where={"document_id": document_id})
        logger.info("Vector store: eliminados los chunks de '%s'.", document_id)

    def count(self) -> int:
        return int(self._collection.count())
