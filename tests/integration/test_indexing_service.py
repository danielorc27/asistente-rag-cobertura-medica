"""Pruebas del pipeline de ingesta (Fase 4, §11.7)."""

from pathlib import Path

import pytest
from app.application.dto.indexing import IndexingMode
from app.application.services.indexing_service import IndexingService
from app.infrastructure.chunking.recursive_chunk_strategy import RecursiveChunkStrategy
from app.infrastructure.document_loader.word_document_loader import WordDocumentLoader
from app.infrastructure.parser.text_normalizer import DefaultTextNormalizer

from tests.mocks.in_memory import (
    DeterministicEmbeddingProvider,
    InMemoryIndexStateRepository,
    InMemoryVectorStore,
)

REAL_DOCUMENTS = Path(__file__).resolve().parents[2] / "documents"


def _service(
    documents_path: Path,
    vector_store: InMemoryVectorStore | None = None,
    index_state: InMemoryIndexStateRepository | None = None,
    chunk_size: int = 1000,
) -> tuple[IndexingService, InMemoryVectorStore, InMemoryIndexStateRepository]:
    store = vector_store or InMemoryVectorStore()
    state = index_state or InMemoryIndexStateRepository()
    service = IndexingService(
        documents_path=documents_path,
        loaders=[WordDocumentLoader()],
        normalizer=DefaultTextNormalizer(),
        chunk_strategy=RecursiveChunkStrategy(chunk_size=chunk_size, chunk_overlap=100),
        embedding_provider=DeterministicEmbeddingProvider(),
        vector_store=store,
        index_state=state,
        embedding_model="fake-model",
        chunk_size=chunk_size,
        chunk_overlap=100,
    )
    return service, store, state


@pytest.mark.integration
class TestIndexingServiceWithRealDocuments:
    def test_full_indexing_of_real_documents(self) -> None:
        service, store, state = _service(REAL_DOCUMENTS)
        report = service.run(IndexingMode.FULL)

        assert len(report.documents_processed) == 3
        assert not report.documents_failed
        assert report.chunks_created > 0
        assert report.embeddings_created == report.chunks_created
        assert store.count() == report.chunks_created
        assert state.manifest is not None
        assert len(state.manifest.documents) == 3
        assert service.is_index_ready()

    def test_incremental_skips_unchanged_documents(self) -> None:
        service, store, state = _service(REAL_DOCUMENTS)
        service.run(IndexingMode.FULL)
        chunks_before = store.count()

        report = service.run(IndexingMode.INCREMENTAL)
        assert not report.documents_processed
        assert len(report.documents_skipped) == 3
        assert store.count() == chunks_before

    def test_new_only_skips_known_documents(self) -> None:
        service, _, _ = _service(REAL_DOCUMENTS)
        service.run(IndexingMode.FULL)
        report = service.run(IndexingMode.NEW_ONLY)
        assert not report.documents_processed

    def test_incompatible_manifest_forces_full(self) -> None:
        service, _, state = _service(REAL_DOCUMENTS)
        service.run(IndexingMode.FULL)
        # Simular cambio de parámetros de chunking: manifiesto incompatible.
        service2, _, _ = _service(REAL_DOCUMENTS, index_state=state, chunk_size=500)
        report = service2.run(IndexingMode.INCREMENTAL)
        assert report.mode is IndexingMode.FULL
        assert len(report.documents_processed) == 3

    def test_chunks_have_traceability_metadata(self) -> None:
        service, store, _ = _service(REAL_DOCUMENTS)
        service.run(IndexingMode.FULL)
        chunk = next(iter(store.records.values())).chunk
        assert chunk.chunk_id
        assert chunk.document_id
        assert chunk.document_name.endswith(".docx")
        assert chunk.total_chunks > 0


@pytest.mark.integration
class TestIndexingServiceEdgeCases:
    def test_empty_and_incompatible_files_are_skipped(self, tmp_path: Path) -> None:
        (tmp_path / "vacio.docx").write_bytes(b"")  # corrupto: no es un docx real
        (tmp_path / "notas.txt").write_text("sin loader", encoding="utf-8")
        service, store, _ = _service(tmp_path)
        report = service.run(IndexingMode.FULL)

        assert report.documents_failed == ["vacio.docx"]
        assert report.documents_skipped == ["notas.txt"]
        assert store.count() == 0

    def test_failed_document_does_not_stop_pipeline(self, tmp_path: Path) -> None:
        import shutil

        shutil.copy(REAL_DOCUMENTS / "DOC1_Manual_de_Beneficios.docx", tmp_path / "valido.docx")
        (tmp_path / "corrupto.docx").write_bytes(b"no es zip")
        service, store, _ = _service(tmp_path)
        report = service.run(IndexingMode.FULL)

        assert "valido.docx" in report.documents_processed
        assert "corrupto.docx" in report.documents_failed
        assert store.count() > 0

    def test_missing_documents_directory(self, tmp_path: Path) -> None:
        service, _, _ = _service(tmp_path / "no_existe")
        report = service.run(IndexingMode.FULL)
        assert not report.documents_processed
        assert not report.documents_failed

    def test_modified_document_is_reindexed(self, tmp_path: Path) -> None:
        import shutil

        target = tmp_path / "doc.docx"
        shutil.copy(REAL_DOCUMENTS / "DOC3_Criterios_de_Necesidad_Medica.docx", target)
        service, store, state = _service(tmp_path)
        service.run(IndexingMode.FULL)

        # Reemplazar por un documento distinto con el mismo nombre → hash distinto.
        shutil.copy(REAL_DOCUMENTS / "DOC1_Manual_de_Beneficios.docx", target)
        report = service.run(IndexingMode.INCREMENTAL)
        assert report.documents_processed == ["doc.docx"]
        # Los chunks anteriores del documento fueron reemplazados, no duplicados.
        doc_ids = {r.chunk.document_id for r in store.records.values()}
        assert doc_ids == {"doc"}
