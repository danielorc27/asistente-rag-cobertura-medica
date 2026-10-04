"""DTOs del pipeline de consulta de cobertura (§7.13, §14.5, §14.7)."""

from pydantic import BaseModel, Field

from app.domain.value_objects.enums import CoverageStatus, EvidenceStrength


class CoverageQuery(BaseModel):
    """Consulta de cobertura (§14.5): identificador estructurado + pregunta."""

    affiliate_id: str = Field(min_length=1, description="Identificador del afiliado (A-#####).")
    question: str = Field(min_length=5, description="Consulta en lenguaje natural.")


class EvidenceItem(BaseModel):
    """Fragmento documental citado en la respuesta (§7.14)."""

    chunk_id: str
    document_name: str
    content: str
    similarity: float | None = None


class CoverageTrace(BaseModel):
    """Metadatos de trazabilidad de la decisión (§7.18, §13.3)."""

    trace_id: str
    model: str | None = None
    prompt_version: str | None = None
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    retrieved_chunks: int = 0


class CoverageResponse(BaseModel):
    """Respuesta estructurada del sistema; nunca texto plano (§7.13)."""

    status: CoverageStatus
    summary: str
    reasoning: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    evidence_strength: EvidenceStrength
    warnings: list[str] = Field(default_factory=list)
    trace: CoverageTrace
