"""Schemas HTTP de administración y diagnóstico."""

from pydantic import BaseModel, Field

from app.application.dto.indexing import IndexingMode, IndexingReport


class ReindexRequest(BaseModel):
    """Cuerpo de POST /reindex."""

    mode: IndexingMode = Field(default=IndexingMode.INCREMENTAL)


class ReindexResponse(BaseModel):
    mode: str
    documents_processed: list[str]
    documents_skipped: list[str]
    documents_failed: list[str]
    chunks_created: int
    embeddings_created: int
    duration_seconds: float

    @classmethod
    def from_application(cls, report: IndexingReport) -> "ReindexResponse":
        return cls(
            mode=report.mode.value,
            documents_processed=report.documents_processed,
            documents_skipped=report.documents_skipped,
            documents_failed=report.documents_failed,
            chunks_created=report.chunks_created,
            embeddings_created=report.embeddings_created,
            duration_seconds=round(report.duration_seconds, 2),
        )


class HealthResponse(BaseModel):
    """Respuesta de GET /health (§9.13)."""

    status: str
    version: str
    vector_store_available: bool
    indexed_chunks: int
    index_ready: bool
    affiliate_repository_available: bool
    llm_configured: bool
