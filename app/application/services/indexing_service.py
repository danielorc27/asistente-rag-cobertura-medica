"""Servicio de indexación documental (§6, Fase 4).

Orquesta: descubrimiento → carga → normalización → validación → hash →
chunking → metadatos → embeddings → persistencia. Un documento que falla
nunca detiene el pipeline (§6.16).

Depende exclusivamente de los contratos del dominio.
"""

import hashlib
import logging
import time
from dataclasses import replace
from pathlib import Path

from app.application.dto.indexing import IndexingMode, IndexingReport
from app.domain.entities.document import Document
from app.domain.exceptions.errors import DomainError
from app.domain.providers.chunk_strategy import ChunkStrategy
from app.domain.providers.document_loader import DocumentLoader
from app.domain.providers.embedding_provider import EmbeddingProvider
from app.domain.providers.text_normalizer import TextNormalizer
from app.domain.providers.vector_store import VectorRecord, VectorStore
from app.domain.repositories.index_state_repository import IndexManifest, IndexStateRepository
from app.domain.value_objects.document_chunk import DocumentChunk
from app.shared.constants.ingestion import MIN_DOCUMENT_LENGTH, PIPELINE_VERSION

logger = logging.getLogger(__name__)


class IndexingService:
    """Construye y mantiene el índice vectorial de documentos."""

    def __init__(
        self,
        documents_path: Path,
        loaders: list[DocumentLoader],
        normalizer: TextNormalizer,
        chunk_strategy: ChunkStrategy,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        index_state: IndexStateRepository,
        embedding_model: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self._documents_path = documents_path
        self._loaders = loaders
        self._normalizer = normalizer
        self._chunk_strategy = chunk_strategy
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._index_state = index_state
        self._embedding_model = embedding_model
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def run(self, mode: IndexingMode) -> IndexingReport:
        """Ejecuta la indexación en el modo solicitado (§6.14)."""
        started = time.perf_counter()
        manifest = self._load_manifest()
        if manifest is None:
            logger.info("Manifiesto ausente o incompatible: se fuerza modo FULL (§14.11).")
            mode = IndexingMode.FULL
            manifest = self._new_manifest()

        if mode is IndexingMode.FULL:
            # reset() y no borrado por documento: al cambiar de proveedor de
            # embeddings también cambia la dimensionalidad de la colección.
            self._vector_store.reset()
            manifest = self._new_manifest()

        report = IndexingReport(mode=mode)
        for path in self._discover():
            self._process_path(path, mode, manifest, report)

        self._index_state.save(manifest)
        report.duration_seconds = time.perf_counter() - started
        logger.info("Indexación finalizada.\n%s", report.summary())
        return report

    def is_index_ready(self) -> bool:
        """Indica si existe un índice compatible con la configuración (§9.8)."""
        return self._load_manifest() is not None and self._vector_store.count() > 0

    # ------------------------------------------------------------------ etapas

    def _discover(self) -> list[Path]:
        """Descubrimiento automático: nunca nombres hardcodeados (§6.4)."""
        if not self._documents_path.exists():
            logger.warning("Directorio de documentos no existe: %s", self._documents_path)
            return []
        return sorted(p for p in self._documents_path.iterdir() if p.is_file())

    def _process_path(
        self,
        path: Path,
        mode: IndexingMode,
        manifest: IndexManifest,
        report: IndexingReport,
    ) -> None:
        loader = next((ld for ld in self._loaders if ld.supports(path)), None)
        if loader is None:
            logger.info("Sin loader compatible para '%s'; se omite.", path.name)
            report.documents_skipped.append(path.name)
            return
        try:
            document = self._prepare(loader.load(path))
        except DomainError as exc:
            logger.error("Documento '%s' falló: %s", path.name, exc)
            report.documents_failed.append(path.name)
            return

        if not self._validate(document):
            report.documents_skipped.append(document.name)
            return

        if not self._needs_indexing(document, mode, manifest):
            logger.info(
                "Documento '%s' sin cambios; se reutiliza el índice (§6.15).", document.name
            )
            report.documents_skipped.append(document.name)
            return

        try:
            chunks = self._build_chunks(document)
            embeddings = self._embedding_provider.embed_texts([c.content for c in chunks])
            self._vector_store.delete_document(document.document_id)
            self._vector_store.upsert(
                [
                    VectorRecord(chunk=c, embedding=e)
                    for c, e in zip(chunks, embeddings, strict=True)
                ]
            )
        except DomainError as exc:
            logger.error("Indexación de '%s' falló: %s", document.name, exc)
            report.documents_failed.append(document.name)
            return

        manifest.documents[document.document_id] = document.content_hash
        report.documents_processed.append(document.name)
        report.chunks_created += len(chunks)
        report.embeddings_created += len(embeddings)

    def _prepare(self, document: Document) -> Document:
        """Normaliza el contenido y calcula el hash (§6.6, §6.11)."""
        content = self._normalizer.normalize(document.content)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return replace(document, content=content, content_hash=content_hash)

    def _validate(self, document: Document) -> bool:
        """Validación previa al chunking (§6.7)."""
        if document.is_empty:
            logger.warning("Documento vacío: '%s'; se omite.", document.name)
            return False
        if len(document.content) < MIN_DOCUMENT_LENGTH:
            logger.warning("Documento demasiado pequeño: '%s'; se omite.", document.name)
            return False
        return True

    def _needs_indexing(
        self, document: Document, mode: IndexingMode, manifest: IndexManifest
    ) -> bool:
        known_hash = manifest.documents.get(document.document_id)
        if mode is IndexingMode.NEW_ONLY:
            return known_hash is None
        # FULL parte de manifiesto vacío; INCREMENTAL compara hashes (§6.11).
        return known_hash != document.content_hash

    def _build_chunks(self, document: Document) -> list[DocumentChunk]:
        pieces = self._chunk_strategy.split(document.content)
        total = len(pieces)
        return [
            DocumentChunk(
                chunk_id=f"{document.document_id}_{index:05d}",
                document_id=document.document_id,
                document_name=document.name,
                source=document.source,
                chunk_index=index,
                total_chunks=total,
                content=piece,
            )
            for index, piece in enumerate(pieces)
        ]

    # -------------------------------------------------------------- manifiesto

    def _load_manifest(self) -> IndexManifest | None:
        manifest = self._index_state.load()
        if manifest is None:
            return None
        if manifest.pipeline_version != PIPELINE_VERSION or not manifest.is_compatible_with(
            self._embedding_model, self._chunk_size, self._chunk_overlap
        ):
            return None
        return manifest

    def _new_manifest(self) -> IndexManifest:
        return IndexManifest(
            embedding_model=self._embedding_model,
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
            pipeline_version=PIPELINE_VERSION,
            documents={},
        )
