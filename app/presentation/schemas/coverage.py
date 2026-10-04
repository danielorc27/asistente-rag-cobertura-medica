"""Schemas HTTP del endpoint de consulta (§4.5: conversión Request/Response)."""

from pydantic import BaseModel, Field

from app.application.dto.coverage import CoverageQuery, CoverageResponse


class QueryRequest(BaseModel):
    """Cuerpo de POST /query (§14.5)."""

    affiliate_id: str = Field(min_length=1, examples=["A-00001"])
    question: str = Field(
        min_length=5,
        examples=["¿La resonancia lumbar ordenada por mi médico está cubierta por mi plan?"],
    )

    def to_application(self) -> CoverageQuery:
        return CoverageQuery(affiliate_id=self.affiliate_id, question=self.question)


class EvidenceSchema(BaseModel):
    chunk_id: str
    document_name: str
    content: str
    similarity: float | None = None


class TraceSchema(BaseModel):
    trace_id: str
    model: str | None = None
    prompt_version: str | None = None
    latency_ms: float | None = None
    retrieved_chunks: int = 0


class QueryResponse(BaseModel):
    """Respuesta de POST /query: siempre estructurada (§7.13)."""

    status: str
    summary: str
    reasoning: str
    evidence: list[EvidenceSchema]
    evidence_strength: str
    warnings: list[str]
    trace: TraceSchema

    @classmethod
    def from_application(cls, response: CoverageResponse) -> "QueryResponse":
        return cls(
            status=response.status.value,
            summary=response.summary,
            reasoning=response.reasoning,
            evidence=[
                EvidenceSchema(
                    chunk_id=item.chunk_id,
                    document_name=item.document_name,
                    content=item.content,
                    similarity=item.similarity,
                )
                for item in response.evidence
            ],
            evidence_strength=response.evidence_strength.value,
            warnings=response.warnings,
            trace=TraceSchema(
                trace_id=response.trace.trace_id,
                model=response.trace.model,
                prompt_version=response.trace.prompt_version,
                latency_ms=response.trace.latency_ms,
                retrieved_chunks=response.trace.retrieved_chunks,
            ),
        )
