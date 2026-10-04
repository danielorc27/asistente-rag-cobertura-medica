"""Prompt Builder de cobertura (§3.17, §8).

Construcción incremental y componible; nunca concatenación dispersa por
los servicios. El prompt es software: se versiona (§8.18).
"""

from typing import Self

from app.domain.entities.affiliate import Affiliate
from app.domain.entities.preliminary_assessment import PreliminaryAssessment
from app.domain.providers.llm_provider import LLMRequest
from app.domain.value_objects.document_chunk import DocumentChunk
from app.domain.value_objects.enums import CoverageStatus

PROMPT_VERSION = "1.0"

_SYSTEM_PROMPT = """\
Eres un asistente de validación de cobertura de planes de salud.
Tu función es determinar si un procedimiento médico solicitado por un afiliado
está cubierto por su plan, utilizando EXCLUSIVAMENTE la evidencia documental
suministrada y los datos estructurados del afiliado.
Priorizas la precisión sobre la creatividad. No realizas suposiciones.
Respondes siempre en español formal."""

_REASONING_INSTRUCTIONS = """\
## Instrucciones de razonamiento
1. Analiza la consulta e identifica el procedimiento solicitado.
2. Relaciona los datos del afiliado (plan, antigüedad, estado, pagos, autorizaciones, preexistencias) con las reglas de la evidencia documental.
3. Verifica periodos de carencia, exclusiones, requisitos de autorización previa, límites y criterios de necesidad médica que apliquen.
4. Considera los hallazgos estructurados ya verificados sobre el afiliado (sección "Hallazgos verificados"): son hechos confirmados, no los contradigas.
5. Identifica conflictos o vacíos de información y decláralos.
6. Construye una conclusión lógica paso a paso antes de decidir."""

_EVIDENCE_RULES = """\
## Reglas de uso de la evidencia
- Solo puedes utilizar los fragmentos suministrados en la sección "Evidencia documental".
- Cada afirmación sobre reglas del plan debe citar el fragmento que la respalda usando su chunk_id.
- Si la evidencia es insuficiente o contradictoria para decidir, indícalo explícitamente.
- Nunca inventes información ni completes reglas incompletas."""

_RESPONSE_FORMAT = f"""\
## Formato de respuesta
Responde ÚNICAMENTE con un objeto JSON válido con esta estructura:
{{{{
  "status": "uno de: {", ".join(s.value for s in CoverageStatus)}",
  "summary": "conclusión breve y formal (1-2 oraciones)",
  "reasoning": "razonamiento completo paso a paso, en español formal",
  "citations": ["chunk_id de cada fragmento utilizado"],
  "warnings": ["advertencias o condiciones relevantes; lista vacía si no aplican"]
}}}}
No incluyas texto fuera del JSON."""

_GUARDRAILS = """\
## Restricciones obligatorias
- No inventes información.
- No asumas cobertura si no existe evidencia que la respalde.
- No respondas utilizando conocimiento externo a la evidencia suministrada.
- La ausencia de evidencia NUNCA se interpreta como aprobación ni como negación: usa status INSUFFICIENT_INFORMATION.
- No modifiques ni cuestiones los datos del afiliado.
- Si el vínculo del afiliado no está activo, la solicitud no procede; explica la razón citando la evidencia disponible."""


class CoveragePromptBuilder:
    """Ensambla el prompt final a partir de componentes (§8.10)."""

    def __init__(self) -> None:
        self._sections: list[str] = []

    def add_reasoning_instructions(self) -> Self:
        self._sections.append(_REASONING_INSTRUCTIONS)
        return self

    def add_evidence_rules(self) -> Self:
        self._sections.append(_EVIDENCE_RULES)
        return self

    def add_affiliate(self, affiliate: Affiliate, assessment: PreliminaryAssessment) -> Self:
        """Datos del afiliado SIN identificadores personales (§9.18)."""
        authorization = affiliate.prior_authorization
        auth_text = (
            f"{authorization.service} (No. {authorization.number}, vigente hasta "
            f"{authorization.valid_until.isoformat()})"
            if authorization
            else "No registra"
        )
        findings = "\n".join(f"- [{f.code.value}] {f.detail}" for f in assessment.findings)
        self._sections.append(
            "## Datos del afiliado (verificados en el sistema)\n"
            f"- Identificador: {affiliate.affiliate_id}\n"
            f"- Edad: {affiliate.age} años\n"
            f"- Tipo de afiliado: {affiliate.member_type.value}"
            f" (parentesco: {affiliate.relationship})\n"
            f"- Plan: {affiliate.plan}\n"
            f"- Antigüedad en el plan: {affiliate.tenure_months} meses\n"
            f"- Estado de afiliación: {affiliate.affiliation_status.value}\n"
            f"- Estado de pagos: {affiliate.payment_status.value}"
            f" (días de mora: {affiliate.days_overdue})\n"
            f"- Autorización previa: {auth_text}\n"
            f"- Preexistencia declarada: "
            f"{affiliate.preexistence_description if affiliate.declared_preexistence else 'No'}\n"
            f"\n## Hallazgos verificados\n{findings}"
        )
        return self

    def add_evidence(self, chunks: list[DocumentChunk]) -> Self:
        blocks = [
            f"[{chunk.chunk_id}] (fuente: {chunk.document_name})\n{chunk.content}"
            for chunk in chunks
        ]
        self._sections.append("## Evidencia documental\n\n" + "\n\n---\n\n".join(blocks))
        return self

    def add_question(self, question: str) -> Self:
        self._sections.append(f"## Consulta del afiliado\n{question}")
        return self

    def add_response_format(self) -> Self:
        self._sections.append(_RESPONSE_FORMAT)
        return self

    def add_guardrails(self) -> Self:
        self._sections.append(_GUARDRAILS)
        return self

    def build(self) -> LLMRequest:
        return LLMRequest(
            system=_SYSTEM_PROMPT,
            user="\n\n".join(self._sections),
            json_output=True,
        )
