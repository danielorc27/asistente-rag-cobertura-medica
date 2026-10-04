"""DTOs del pipeline de ingesta (§6.18)."""

from enum import StrEnum

from pydantic import BaseModel, Field


class IndexingMode(StrEnum):
    """Modos de reindexación (§6.14)."""

    FULL = "FULL"
    INCREMENTAL = "INCREMENTAL"
    NEW_ONLY = "NEW_ONLY"


class IndexingReport(BaseModel):
    """Resumen de una ejecución de indexación."""

    mode: IndexingMode
    documents_processed: list[str] = Field(default_factory=list)
    documents_skipped: list[str] = Field(default_factory=list)
    documents_failed: list[str] = Field(default_factory=list)
    chunks_created: int = 0
    embeddings_created: int = 0
    duration_seconds: float = 0.0

    def summary(self) -> str:
        return (
            f"Documentos procesados: {len(self.documents_processed)}\n"
            f"Documentos omitidos: {len(self.documents_skipped)}\n"
            f"Documentos con error: {len(self.documents_failed)}\n"
            f"Chunks generados: {self.chunks_created}\n"
            f"Embeddings creados: {self.embeddings_created}\n"
            f"Tiempo total: {self.duration_seconds:.1f} s"
        )
